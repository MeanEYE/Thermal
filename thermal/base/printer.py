import re


def iter_atoms(text):
	"""Split a line into atoms, yielding `(chunk, width)` pairs. Command
	sequences produced by components and markup, and control characters,
	have zero width; printable characters have width one. Lets wrapping
	and padding ignore commands and never break inside of them."""
	index = 0
	end = len(text)

	while index < end:
		start = index
		char = text[index]
		following = text[index + 1] if index + 1 < end else ''

		if char == '\x1b':
			if following == 'D':
				terminator = text.find('\x00', index)
				index = end if terminator < 0 else terminator + 1
			elif following in '2@':
				index += 2
			elif following == '(' and index + 4 < end:
				index += 5 + ord(text[index + 3]) + ord(text[index + 4]) * 256
			else:
				index += 3
			yield text[start:index], 0

		elif char == '\x1d':
			if following == '(' and index + 4 < end:
				index += 5 + ord(text[index + 3]) + ord(text[index + 4]) * 256
			elif following == 'W':
				index += 4
			elif following == 'v' and index + 7 < end:
				columns = ord(text[index + 4]) + ord(text[index + 5]) * 256
				rows = ord(text[index + 6]) + ord(text[index + 7]) * 256
				index += 8 + columns * rows
			elif following == 'k' and index + 2 < end:
				if ord(text[index + 2]) <= 6:
					terminator = text.find('\x00', index + 3)
					index = end if terminator < 0 else terminator + 1
				else:
					index += 4 + (ord(text[index + 3]) if index + 3 < end else 0)
			else:
				index += 3
			yield text[start:index], 0

		elif char < ' ':
			index += 1
			yield char, 0

		else:
			index += 1
			yield char, 1


def visible_length(text):
	"""Number of printable characters in a line, ignoring command
	sequences. Tabs count as zero width."""
	return sum(width for _, width in iter_atoms(text))


class Printer:
	"""Base printer class which can be inherited or used as is."""
	CR = '\x0D'
	LF = '\x0A'
	ESC = '\x1B'
	GS = '\x1D'
	INIT_PRINTER = '\x1B\x40'
	TAB = '\x09'

	# printer specification
	print_area = 384
	supports_cutting = False
	cut_feed_units = 0  # extra motion units to feed past cutting position before cut
	default_code_page = 0
	legacy_graphics = True

	# width of text in dots
	font_normal = 12
	font_double = 24

	def __init__(self, connection):
		self.connection = connection
		self.upside_down = False

	@classmethod
	def __parse_font(self, match, string):
		"""Return string for setting font type."""
		values = match.groupdict()
		return f'{self.ESC}M' + values['number']

	@classmethod
	def __parse_size(self, match, string):
		"""Return string for setting character size."""
		values = match.groupdict()
		width = values['width'] or 1
		height = values['height'] or 1
		value = chr(16 * int(width) + int(height))
		return f'{self.GS}!{value}'

	@classmethod
	def __parse_image(self, match, string):
		"""Return string for printing download graphics by id, with
		optional scale. Printer only honours this at the beginning of a
		line, `Text` takes care of placing it there."""
		values = match.groupdict()
		image_id = values['id']
		x_scale = chr(int(values['x'] or 1))
		y_scale = chr(int(values['y'] or 1))
		return f'{self.GS}(L\x06\x000U{image_id}{x_scale}{y_scale}'

	@classmethod
	def parse(cls, string):
		"""Parse string and replace common formatting commands."""
		replacements = {
				'em': f'{cls.ESC}E1',
				'/em': f'{cls.ESC}E0',
				'st': f'{cls.ESC}G1',
				'/st': f'{cls.ESC}G0',
				'u': f'{cls.ESC}-1',
				'u2': f'{cls.ESC}-2',
				'/u': f'{cls.ESC}-0',
				'inv': f'{cls.GS}B1',
				'/inv': f'{cls.GS}B0',
				'smooth': f'{cls.GS}b1',
				'/smooth': f'{cls.GS}b0',
				'r0': f'{cls.ESC}V0{cls.ESC}{{\x00',  # clears both 90 degree and upside-down
				'r90': f'{cls.ESC}V1',
				'r180': f'{cls.ESC}{{\x01',  # upside-down, only at the beginning of a line
				'r270': f'{cls.ESC}V3',
				'align l': f'{cls.ESC}a\x00',
				'align c': f'{cls.ESC}a\x01',
				'align r': f'{cls.ESC}a\x02',
				'tab': f'{cls.TAB}',
				'/size': f'{cls.GS}!\x00',
				}
		parsers = (
			 (r'\[font (?P<number>\d{1})\]', cls.__parse_font),
			 (r'\[size (?P<width>\d{1,2})(?:,(?P<height>\d{1,2}))?\]', cls.__parse_size),
			 (r'\[img (?P<id>[^\]\s]{2})(?: (?P<x>[12]),(?P<y>[12]))?\]', cls.__parse_image)
			 )

		# replace instances
		result = string
		for tag, value in replacements.items():
			try:
				result = result.replace('[' + tag + ']', value)
			except Exception as error:
				print(f'Error parsing {tag}, with value {value}: '+repr(error))
				break

		# replace instances with parsers
		for expression, callback in parsers:
			r = re.compile(expression)
			while match := r.search(result):
				replacement_value = callback(match, result)
				result = replacement_value.join((
						result[:match.start()],
						result[match.end():]
						))

		return result

	def reset(self):
		"""Reset printer to default configuration."""
		self.connection.write(self.INIT_PRINTER)
		self.upside_down = False

	def set_default_line_spacing(self):
		"""Set default line spacing in dots."""
		return f'{self.ESC}2'

	def set_line_spacing(self, spacing=8):
		"""Set line spacing in dots."""
		return f'{self.ESC}3' + chr(spacing)

	def set_tab_stops(self, tab_stops=None):
		"""Return string for setting horizontal tab positions, in characters
		from the left margin. Positions must be ascending, between 1 and 255,
		at most 32 of them. Without positions all tab stops are cancelled."""
		tab_stops = tuple(tab_stops or ())
		if len(tab_stops) > 32:
			raise ValueError('Printer supports at most 32 tab stops.')

		positions = ''
		previous = 0
		for position in tab_stops:
			if not previous < position <= 255:
				raise ValueError(
						f'Tab stop {position} must be greater than previous '
						f'stop {previous} and at most 255.'
						)
			positions += chr(position)
			previous = position

		return f'{self.ESC}D{positions}\x00'

	def set_smoothing(self, enabled=True):
		"""Return string for turning smoothing on or off. Printer smooths
		edges of characters enlarged with character size command, normal
		size text and graphics are not affected."""
		return f'{self.GS}b' + chr(1 if enabled else 0)

	def set_upside_down(self, enabled=True):
		"""Return string for turning upside-down print mode on or off. Printer
		rotates each following line by 180 degrees, order of lines is not
		changed. Only honoured at the beginning of a line."""
		self.upside_down = enabled
		return f'{self.ESC}{{' + chr(1 if enabled else 0)

	def set_alignment(self, alignment=0):
		"""Return string for setting alignment, 0 - left, 1 - center, 2 - right.
		Printer only honours this at the beginning of a line."""
		return f'{self.ESC}a' + chr(alignment)

	def set_code_page(self, code_page):
		"""Return string for setting code page."""
		return f'{self.ESC}t' + chr(code_page)

	def line_feed(self, count=1):
		"""Print and feed number of lines."""
		self.connection.write(f'{self.ESC}d' + chr(count))
		self.connection.write(self.LF)

	def line_feed_in_units(self, count=1):
		"""Print and feed number of motion units."""
		times = [255,] * (count // 255)
		times.append(count % 255)

		buffer = ''.join([f'{self.ESC}J' + chr(c) for c in times])
		self.connection.write(buffer.encode('latin1'))

	def reverse_line_feed(self, count=1):
		"""Print and reverse feed number of lines."""
		self.connection.write(f'{self.ESC}e' + chr(count))

	def reverse_line_feed_in_units(self, count=1):
		"""Print and feed number of motion units."""
		times = [255,] * (count // 255)
		times.append(count % 255)

		buffer = ''.join([f'{self.ESC}K' + chr(c) for c in times])
		self.connection.write(buffer.encode('latin1'))

	def get_width(self):
		"""Get maximum number of characters we can fit horizontally."""
		return int(self.print_area / self.font_normal)

	def connect(self):
		"""Connect printer."""
		self.connection.connect()

	def disconnect(self):
		"""Disconnect printer."""
		self.connection.close()

	def print(self, buffer):
		"""Send buffer to active connection for printing."""
		self.connection.write(buffer)

	def cut_paper(self, partial=True, feed=None):
		"""Cut paper partially or in entirety. With `feed` printer first feeds
		paper to the cutting position plus that many motion units (GS V 65/66),
		without it paper is cut at the current position (GS V 0/1)."""
		if feed is None:
			command = f'{self.GS}V' + ('1' if partial else '0')
		else:
			feed = max(0, min(int(feed), 255))
			command = f'{self.GS}V' + ('B' if partial else 'A') + chr(feed)

		self.connection.write(command.encode('latin1'))

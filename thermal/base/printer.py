import re


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
	default_code_page = 0
	offset_lines = 3  # number of lines to feed before print is fully visible
	offset_units = 350
	legacy_graphics = True

	# width of text in dots
	font_normal = 12
	font_double = 24

	def __init__(self, connection):
		self.connection = connection

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
		"""Return string for including image type."""
		values = match.groupdict()
		image_id = values['id']
		return f'{self.GS}(L\x06\x000E{image_id}\x01\x01'

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
				'r0': f'{cls.ESC}V0',
				'r90': f'{cls.ESC}V1',
				'r180': f'{cls.ESC}V2',
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
			 (r'\[img (?P<id>[a-zA-z0-9]+)?\]', cls.__parse_image)
			 )

		# replace instances
		result = string
		for tag, value in replacements.items():
			result = result.replace('[' + tag + ']', value)

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

	def set_default_line_spacing(self):
		"""Set default line spacing in dots."""
		return f'{self.ESC}2'

	def set_line_spacing(self, spacing=8):
		"""Set line spacing in dots."""
		return f'{self.ESC}3' + chr(spacing)

	def set_tab_stops(self, tab_stops=None):
		"""Set positions of tab stops."""
		positions = ''
		for position in tab_stops:
			if 0 > position > 255: continue
			positions += chr(position)
		return f'{self.ESC}D{positions}\x00'

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

	def cut_paper(self, partial=True):
		"""If supported paper will be cut partially or in entirety."""
		option = '1' if partial else '0'
		self.connection.write(f'{self.GS}V{option}')

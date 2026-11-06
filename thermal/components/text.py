import re

from ..base.component import Component


class Text(Component):
	"""Simple text component which supports text wrapping and
	clipping. Component can be used to keep variable text as well
	as used like title. Content is always parsed before being
	printed.

	Tabs (`[tab]` markup) are sent to the printer which advances to
	the next tab stop. Stops default to every 8 characters and can be
	changed with `set_tab_stops`. Wrapping takes stops into account.

	Image references (`[img id]` markup) are printed by the printer only
	at the beginning of a line, so they break the line: text before the
	reference ends its line, image is printed, text after continues on
	the following line."""

	DEFAULT_TAB_STOPS = tuple(range(8, 256, 8))

	# download graphics print command produced by `[img id]` markup
	IMAGE_COMMAND = re.compile(r'(\x1d\(L\x06\x000U..[\x01\x02][\x01\x02])')

	def __init__(self, text):
		self.value = text
		self.code_page = None
		self.tab_stops = None

	def set_code_page(self, code_page):
		"""Set encoding for this bit of text."""
		self.code_page = code_page

	def set_tab_stops(self, tab_stops):
		"""Set tab stop positions, in characters from the left margin, used
		by this text. Positions must be ascending, 1 to 255, at most 32.
		Printer keeps them until next change or report print."""
		self.tab_stops = tuple(tab_stops)

	def set_text(self, value):
		"""Set value of the text container."""
		self.value = value

	def __wrap(self, text, width, tab_stops):
		"""Wrap text to width honouring tab stops. Runs of spaces are kept
		mid-line and dropped at line boundaries, words longer than width
		are broken, tab with no stop left on the line breaks the line."""
		lines = []
		line = ''
		column = 0

		def flush():
			nonlocal line, column
			lines.append(line.rstrip(' '))
			line, column = '', 0

		# other whitespace is treated as plain space, tabs are kept
		text = re.sub(r'[\n\r\x0b\x0c]', ' ', text)

		for index, segment in enumerate(text.split('\t')):
			if index > 0:
				next_stop = next((stop for stop in tab_stops if stop > column), None)
				if next_stop is None or next_stop >= width:
					flush()
				else:
					line += '\t'
					column = next_stop

			for token in re.split(r'( +)', segment):
				if not token:
					continue

				if token[0] == ' ':
					if column == 0:
						continue  # drop leading whitespace
					if column + len(token) > width:
						flush()  # drop trailing whitespace
					else:
						line += token
						column += len(token)
					continue

				while token:
					room = width - column
					if len(token) <= room:
						line += token
						column += len(token)
						break

					if column == 0:
						# word longer than width, break it
						line += token[:room]
						token = token[room:]
					flush()

		if line:
			flush()

		return lines

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		printer = self.printer
		tab_stops = self.tab_stops or self.DEFAULT_TAB_STOPS

		# wrap text between image references separately, each image
		# command must start a line and following text goes after it
		text = []
		image_command = ''
		for index, part in enumerate(self.IMAGE_COMMAND.split(printer.parse(self.value))):
			if index % 2 == 1:
				image_command = part
				continue

			lines = self.__wrap(part, width, tab_stops)
			if image_command:
				if lines:
					lines[0] = image_command + lines[0]
				else:
					lines = [image_command,]
				image_command = ''
			text.extend(lines)

		if not text:
			return text

		# apply tab stops if needed, validated by printer
		if self.tab_stops is not None:
			text[0] = printer.set_tab_stops(self.tab_stops) + text[0]

		# apply code pages if needed
		if self.code_page is not None:
			text[0] = printer.set_code_page(self.code_page) + text[0]
			text[-1] = text[-1] + printer.set_code_page(printer.default_code_page)

		return text

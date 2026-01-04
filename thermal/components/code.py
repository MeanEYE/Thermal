from ..base.component import Component


class Code(Component):
	"""Abstract class for implementing various 2D and bar codes."""

	def __init__(self, data, code_type):
		self.align = 1
		self.data = data
		self.code_type = code_type

	def set_align(self, alignment):
		"""Set alignment on the paper left being 0, center 1, right 2."""
		if 0 <= alignment <= 2:
			self.align = alignment

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		raise NotImplemented()


class BarCode(Code):
	"""Implementation of various binary and similar bar codes."""

	def __init__(self, data, code_type):
		Code.__init__(self, data, code_type)

		self.width = None
		self.height = None
		self.text_position = None
		self.text_font = None

	def set_height(self, height):
		"""Set code height in dots."""
		if 12 <= height <= 160:
			self.height = height

	def set_width(self, width):
		"""Set code width scale."""
		if 0 <= width <= 4:
			self.width = width

	def set_text_position(self, position):
		"""Set HRI text position in relation to code."""
		if 0 <= position <= 2:
			self.text_position = position

	def set_text_font(self, font):
		"""Set HRI text font to A(1) or B(2)."""
		if 0 <= font <= 1:
			self.text_font = font

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		lines = []
		printer = self.printer

		# apply bar code properties
		if self.height:
			lines.append(f'{printer.GS}h' + chr(self.height))
		if self.width:
			lines.append(f'{printer.GS}w' + chr(self.width))
		if self.text_position:
			lines.append(f'{printer.GS}H{self.text_position}')
		if self.text_font:
			lines.append(f'{printer.GS}f{self.text_font}')

		# set alignment
		lines.append(f'{printer.ESC}a{self.align}')

		# print bar code
		if 0 <= ord(self.code_type) <= 6:
			lines.append(f'{printer.GS}\x6B{self.code_type}{self.data}\x00')
		else:
			length = chr(len(self.data))
			lines.append(f'{printer.GS}\x6B{self.code_type}{length}{self.data}')

		return [''.join(lines),]


class MatrixCode(Code):
	"""Implementation of various binary and similar bar codes."""

	PDF417 = 0  # currently not used
	DATA_MATRIX = 1
	QR_CODE = 2

	def __init__(self, data, code_type=2):
		Code.__init__(self, data, code_type)

		self.error_correction = 1
		self.module_size = 6

	def set_error_correction(self, level):
		"""Set error correction level."""
		if 1 <= level <= 4:
			self.error_correction = level

	def set_module_size(self, size=4):
		"""Change size of each module in dots."""
		if 1 <= size <= 30:
			self.module_size = size

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		lines = []
		printer = self.printer

		# prepare parameters
		total_bytes = len(self.data) + 3
		size_h = (total_bytes >> 8) & 0xff
		size_l = total_bytes & 0xff

		# store data to printer memory
		data_size = chr(size_l) + chr(size_h)
		lines.append(f'{printer.GS}(k{data_size}\x31\x50\x30' + self.data)

		# set qr code properties
		lines.append(f'{printer.GS}(k\x03\x00\x31\x45' + chr(ord('\x29') + self.error_correction))
		lines.append(f'{printer.GS}(k\x03\x00\x31\x43' + chr(self.module_size))

		# actually print code
		lines.append(f'{printer.ESC}a{self.align}')
		lines.append(f'{printer.GS}(k\x03\x00\x31\x51\x30')

		return [''.join(lines),]


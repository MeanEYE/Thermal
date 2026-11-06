from ..base.component import Component


class Code(Component):
	"""Abstract class for implementing various 2D and bar codes."""

	ALIGN_LEFT = 0
	ALIGN_CENTER = 1
	ALIGN_RIGHT = 2

	def __init__(self, data, code_type):
		Component.__init__(self)
		self.align = self.ALIGN_CENTER
		self.data = data
		self.code_type = code_type

	def set_data(self, data):
		"""Set data to be encoded."""
		self.data = data

	def set_align(self, alignment):
		"""Set alignment on the paper left being 0, center 1, right 2."""
		if 0 <= alignment <= 2:
			self.align = alignment

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		raise NotImplemented()


class BarCode(Code):
	"""Implementation of one dimensional bar codes through `GS k`.
	Symbology constants use function B form (length prefixed data)."""

	# symbologies, value is `m` parameter of GS k
	UPC_A = 65
	UPC_E = 66
	EAN13 = 67  # also known as JAN13
	EAN8 = 68   # also known as JAN8
	CODE39 = 69
	ITF = 70
	CODABAR = 71
	CODE93 = 72
	CODE128 = 73  # data must start with code set, `{A`, `{B` or `{C`; `{B` is added if missing
	GS1_128 = 74

	# human readable text position
	TEXT_NONE = 0
	TEXT_ABOVE = 1
	TEXT_BELOW = 2
	TEXT_BOTH = 3

	# human readable text font
	FONT_A = 0
	FONT_B = 1

	def __init__(self, data, code_type=CODE128):
		Code.__init__(self, data, ord(code_type) if isinstance(code_type, str) else code_type)

		self.width = None
		self.height = None
		self.text_position = None
		self.text_font = None

	def set_height(self, height):
		"""Set code height in dots."""
		if 12 <= height <= 160:
			self.height = height

	def set_width(self, width):
		"""Set module width in dots, 2 to 6."""
		if 2 <= width <= 6:
			self.width = width

	def set_text_position(self, position):
		"""Set HRI text position in relation to code, see `TEXT_*`."""
		if 0 <= position <= 3:
			self.text_position = position

	def set_text_font(self, font):
		"""Set HRI text font, see `FONT_*`."""
		if 0 <= font <= 1:
			self.text_font = font

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		lines = []
		printer = self.printer
		data = self.data

		# apply bar code properties
		if self.height:
			lines.append(f'{printer.GS}h' + chr(self.height))
		if self.width:
			lines.append(f'{printer.GS}w' + chr(self.width))
		if self.text_position:
			lines.append(f'{printer.GS}H' + chr(self.text_position))
		if self.text_font:
			lines.append(f'{printer.GS}f' + chr(self.text_font))

		# code 128 requires code set selection at the start of data
		if self.code_type == self.CODE128 and not data.startswith('{'):
			data = '{B' + data

		# set alignment
		lines.append(printer.set_alignment(self.align))

		# print bar code, function A types are NUL terminated while
		# function B types are prefixed with data length
		if 0 <= self.code_type <= 6:
			lines.append(f'{printer.GS}k{chr(self.code_type)}{data}\x00')
		else:
			lines.append(f'{printer.GS}k{chr(self.code_type)}{chr(len(data))}{data}')

		return [''.join(lines),]


class MatrixCode(Code):
	"""Implementation of two dimensional codes through `GS ( k`. Supported
	types are QR code, PDF417 and Data Matrix (ECC200)."""

	# code types, value is `cn` parameter of GS ( k
	PDF417 = 48
	QR_CODE = 49
	DATA_MATRIX = 54

	# QR code error correction levels, roughly 7%, 15%, 25% and 30%
	ERROR_L = 1
	ERROR_M = 2
	ERROR_Q = 3
	ERROR_H = 4

	# QR code models
	QR_MODEL_1 = 49
	QR_MODEL_2 = 50
	MICRO_QR = 51

	def __init__(self, data, code_type=QR_CODE):
		Code.__init__(self, data, code_type)

		self.error_correction = None
		self.module_size = None
		self.model = self.QR_MODEL_2
		self.columns = 0  # PDF417 and Data Matrix, 0 is automatic
		self.rows = 0
		self.row_height = 3  # PDF417 only
		self.truncated = False  # PDF417 only

	def set_error_correction(self, level):
		"""Set error correction level. For QR code one of `ERROR_*` (1 to 4),
		for PDF417 level 0 to 8. Data Matrix has fixed error correction."""
		self.error_correction = level

	def set_module_size(self, size=4):
		"""Change size of each module in dots. QR code 1 to 16, PDF417 2 to 8,
		Data Matrix 2 to 16."""
		self.module_size = size

	def set_model(self, model):
		"""Set QR code model, see `QR_MODEL_*` and `MICRO_QR`."""
		self.model = model

	def set_size(self, columns=0, rows=0):
		"""Set number of columns and rows for PDF417 or Data Matrix, 0 lets
		the printer decide. PDF417 columns 0 to 30, rows 0 or 3 to 90."""
		self.columns = columns
		self.rows = rows

	def set_row_height(self, height):
		"""Set PDF417 row height in modules, 2 to 8."""
		self.row_height = height

	def set_truncated(self, truncated=True):
		"""Print truncated PDF417, without right side row indicators."""
		self.truncated = truncated

	def __check(self, name, value, low, high):
		"""Raise if value is outside of range."""
		if not low <= value <= high:
			raise ValueError(f'{name} must be between {low} and {high}, got {value}.')

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		printer = self.printer
		code_type = chr(self.code_type)

		def command(function, parameters):
			"""Build GS ( k command with proper size for this code type."""
			size = len(parameters) + 2
			return f'{printer.GS}(k{chr(size % 256)}{chr(size // 256)}{code_type}{function}{parameters}'

		lines = []

		if self.code_type == self.QR_CODE:
			error_correction = self.error_correction or self.ERROR_L
			module_size = self.module_size or 6
			self.__check('Error correction', error_correction, 1, 4)
			self.__check('Module size', module_size, 1, 16)

			lines.append(command('A', chr(self.model) + '\x00'))
			lines.append(command('C', chr(module_size)))
			lines.append(command('E', chr(47 + error_correction)))

		elif self.code_type == self.PDF417:
			module_size = self.module_size or 3
			self.__check('Columns', self.columns, 0, 30)
			if self.rows: self.__check('Rows', self.rows, 3, 90)
			self.__check('Module size', module_size, 2, 8)
			self.__check('Row height', self.row_height, 2, 8)

			lines.append(command('A', chr(self.columns)))
			lines.append(command('B', chr(self.rows)))
			lines.append(command('C', chr(module_size)))
			lines.append(command('D', chr(self.row_height)))
			if self.error_correction is not None:
				self.__check('Error correction', self.error_correction, 0, 8)
				lines.append(command('E', '0' + chr(48 + self.error_correction)))
			lines.append(command('F', chr(1 if self.truncated else 0)))

		elif self.code_type == self.DATA_MATRIX:
			module_size = self.module_size or 6
			self.__check('Module size', module_size, 2, 16)

			lines.append(command('B', '\x00' + chr(self.rows) + chr(self.columns)))
			lines.append(command('C', chr(module_size)))

		else:
			raise ValueError(f'Unsupported matrix code type {self.code_type}.')

		# store data to printer memory, align and print
		lines.append(command('P', '0' + self.data))
		lines.append(printer.set_alignment(self.align))
		lines.append(command('Q', '0'))

		return [''.join(lines),]

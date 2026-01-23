
from ..base.component import Component


class Image(Component):
	"""Base class for handling image operations with ESCPOS terminals."""
	image_counter = 0

	def __init__(self, image_id=None, data=None, width=0, height=0):
		self.data = data
		self.width = width
		self.height = height
		self.scale_x = 1
		self.scale_y = 1
		self.image_cached = False
		self.alignment = None

		if image_id:
			self.image_id = image_id[:2]
		else:
			self.image_id = hex(self.image_counter)[2:4].zfill(2)
			self.image_counter += 1

	def __get_int_in_bytes(self, value):
		"""Return low and high bytes for single integer."""
		return value % 256, value // 256

	def set_scale(self, x=1, y=1):
		"""Set scaling factor. It can be either 1x or 2x."""
		self.scale_x = x
		self.scale_y = y

	def set_data_bytes(self, data, width, height):
		"""Set data for printing."""
		self.data = data
		self.width = width
		self.height = height
		self.image_cached = False

	def set_image_id(self, image_id):
		"""Set unique image id. This allows us to upload to printer once per
		session or even fewer times."""
		self.image_id = image_id[:2]
		self.image_cached = False

	def set_alignment(self, align):
		"""
		Set image alignment on the page.
		0 - left, 1 - center, 2 - right
		"""
		assert 0 <= align <= 2
		self.alignment = align

	def get_width_bytes(self):
		"""Return image width in two (low, high) bytes."""
		assert self.width > 0
		return self.__get_int_in_bytes(self.width)

	def get_lines(self, width):
		"""Prepare lines from binary data and return them for printing."""
		result = []
		printer = self.printer

		tone = '0'
		colors = '\x01'
		print_color = '1'
		x_scale = chr(self.scale_x)
		y_scale = chr(self.scale_y)

		# prepare image size
		width = self.__get_int_in_bytes(self.width)
		height = self.__get_int_in_bytes(self.height)
		image_size = chr(width[0]) + chr(width[1]) + chr(height[0]) + chr(height[1])

		# prepare header
		header = f'{tone}{self.image_id}{colors}{image_size}{print_color}'
		total_size = self.__get_int_in_bytes(len(header) + len(self.data)+ 2)
		data_size = chr(total_size[0]) + chr(total_size[1])

		# upload image to printer and cache it using unique id
		if not self.image_cached:
			result.append(f'{printer.GS}(L{data_size}0C{header}' + self.data.decode('latin1'))
			self.image_cached = True

		# align image if requested
		if self.alignment is not None:
			result.append(f'{printer.ESC}a' + chr(self.alignment) + printer.LF)

		# tell printer to print image with specified id
		result.append(f'{printer.GS}(L\x06\x000E{self.image_id}{x_scale}{y_scale}')

		return result

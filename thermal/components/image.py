import os

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
			self.image_id = f'{Image.image_counter % 256:02x}'
			Image.image_counter += 1

	def on_printer_reset(self):
		"""Printer reset discards download graphics on some models, upload again."""
		self.image_cached = False

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

	def load_from_pbm(self, path):
		"""Load image data from PBM format."""
		assert os.path.exists(path)
		result = False

		with open(path, 'rb') as raw_file:
			magic = raw_file.readline().strip()
			dimensions = raw_file.readline().strip().split(b' ')
			image_width, image_height = int(dimensions[0]), int(dimensions[1])
			data = raw_file.read()

		if magic == b'P4':
			# no conversion needed
			self.width = image_width
			self.height = image_height
			self.data = data
			result = True

		elif magic == b'P1':
			# needs packing
			self.width = image_width
			self.height = image_height

			# prepare for bit packing
			output = bytearray()
			output_bits = 0
			character = 0

			# walk through file ignoring anything other than 0 and 1 and
			# shifting current bit setting marker. If width is not divisible
			# by eight, remaining bits are ignored and treated as 0.
			for digit in data:
				if digit not in (48, 49): continue

				position = 7 - (output_bits % 8)
				character |= (digit - 48) << position
				output_bits += 1

				if output_bits == image_width:
					output.append(character)
					output_bits = 0
					character = 0

				if position == 0:
					output.append(character)
					character = 0

			self.data = output

		return result

	def __print_modern(self, width):
		"""Print using modern command."""
		result = ''
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

		# upload image to printer RAM (download graphics, fn 83) and
		# cache it using unique id; NV graphics (fn 67) would wear flash
		if not self.image_cached:
			result += f'{printer.GS}(L{data_size}0S{header}' + self.data.decode('latin1')
			self.image_cached = True

		# align image if requested, report resets alignment after component
		if self.alignment is not None:
			result += printer.set_alignment(self.alignment)

		# tell printer to print download graphics with specified id (fn 85)
		result += f'{printer.GS}(L\x06\x000U{self.image_id}{x_scale}{y_scale}'

		return [result,]

	def __print_legacy(self, width):
		"""Print using legacy method."""
		result = ''
		printer = self.printer

		truth_table = { (1, 1): '0', (2, 1): '1', (1, 2): '2', (2, 2): '3' }
		scale = truth_table[(self.scale_x, self.scale_y)]

		# prepare image size
		width = self.__get_int_in_bytes((self.width + 7) // 8)
		height = self.__get_int_in_bytes(self.height)
		image_size = chr(width[0]) + chr(width[1]) + chr(height[0]) + chr(height[1])

		# align image if requested, report resets alignment after component
		if self.alignment is not None:
			result += printer.set_alignment(self.alignment)

		# print data
		result += f'{printer.GS}v0{scale}{image_size}' + self.data.decode('latin1')

		return [result,]

	def get_lines(self, width):
		"""Prepare lines from binary data and return them for printing."""
		return self.__print_legacy(width) if self.printer.legacy_graphics else self.__print_modern(width)

from ..base.component import Component


class Border(Component):
	"""Simple component that draws border around content."""
	v_chars = (' ', '\xB3', '\xBA')
	h_chars = (' ', '\xC4', '\xCD')

	top_cell = (' ', '\xC2', '\xD1')
	middle_cell = (' ', '\xC5', '\xD8')
	bottom_cell = (' ', '\xC1', '\xCF')
	footer_cell = {
			'l': (' ', '\xC3', '\xCC'),
			'r': (' ', '\xB4', '\xB9'),
			}

	corners = {
		'tl': {'00': '\x00', '10': '\xDA', '11': '\xDA', '12': '\xD6', '21': '\xD5', '22': '\xC9'},
		'tr': {'00': '\x00', '10': '\xBF', '11': '\xBF', '12': '\xB7', '21': '\xB8', '22': '\xBB'},
		'bl': {'00': '\x00', '10': '\xC0', '11': '\xC0', '12': '\xD3', '21': '\xD4', '22': '\xC8'},
		'br': {'00': '\x00', '10': '\xD9', '11': '\xD9', '12': '\xBD', '21': '\xBE', '22': '\xBC'},
		}

	def __init__(self, component, border=None):
		self.component = component
		self.border = border or (1, 1, 1, 1)
		self.code_page = None

	def set_code_page(self, code_page):
		"""Set code page for content inside the border. Box characters
		stay in printer's default page."""
		self.code_page = code_page

	def set_printer(self, printer):
		"""Set printer to be used for various calculations."""
		Component.set_printer(self, printer)
		self.component.set_printer(printer)

	def on_printer_reset(self):
		"""Forward printer reset to contained component."""
		self.component.on_printer_reset()

	def set_component(self, component):
		"""Set component for rendering."""
		self.component = component

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		top_border, right_border, bottom_border, left_border = self.border
		top = list(self.h_chars[top_border] * width)
		bottom = list(self.h_chars[bottom_border] * width)
		right = self.v_chars[right_border]
		left = self.v_chars[left_border]

		top[0] = self.corners['tl'][f'{top_border}{left_border}']
		top[-1] = self.corners['tr'][f'{top_border}{right_border}']
		bottom[0] = self.corners['bl'][f'{bottom_border}{left_border}']
		bottom[-1] = self.corners['br'][f'{bottom_border}{right_border}']

		top = self.printer.set_line_spacing(0) + ''.join(top)
		bottom = ''.join(bottom)

		# apply them to content, switching code page around it if requested
		if self.code_page is not None:
			page_on = self.printer.set_code_page(self.code_page)
			page_off = self.printer.set_code_page(self.printer.default_code_page)
		else:
			page_on = page_off = ''

		lines = self.component.get_lines(width - 2)
		lines = [left + page_on + line.ljust(width - 2) + page_off + right for line in lines]
		lines.insert(0, top)
		lines.append(bottom)

		return lines

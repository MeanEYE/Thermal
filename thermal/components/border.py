from ..base.component import Component


class Border(Component):
	"""Simple component that draws border around content."""

	def __init__(self, component, border=None):
		self.component = component
		self.border = border or (1, 1, 1, 1)

	def set_printer(self, printer):
		"""Set printer to be used for various calculations."""
		Component.set_printer(self, printer)
		self.component.set_printer(printer)

	def set_component(self, component):
		"""Set component for rendering."""
		self.component = component

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		v_chars = (' ', '\xB3', '\xBA')
		h_chars = (' ', '\xC4', '\xCD')

		corners = {
			'tl': {'00': '\x00', '10': '\xDA', '11': '\xDA', '12': '\xD6', '21': '\xD5', '22': '\xC9'},
			'tr': {'00': '\x00', '10': '\xBF', '11': '\xBF', '12': '\xB7', '21': '\xB8', '22': '\xBB'},
			'bl': {'00': '\x00', '10': '\xC0', '11': '\xC0', '12': '\xD3', '21': '\xD4', '22': '\xC8'},
			'br': {'00': '\x00', '10': '\xD9', '11': '\xD9', '12': '\xBD', '21': '\xBE', '22': '\xBC'},
			}

		# prepare characters
		top_border, right_border, bottom_border, left_border = self.border
		top = list(h_chars[self.border[0]] * width)
		bottom = list(h_chars[self.border[2]] * width)
		right = v_chars[self.border[1]]
		left = v_chars[self.border[3]]

		top[0] = corners['tl'][f'{top_border}{left_border}']
		top[-1] = corners['tr'][f'{top_border}{right_border}']
		bottom[0] = corners['bl'][f'{bottom_border}{left_border}']
		bottom[-1] = corners['br'][f'{bottom_border}{right_border}']

		top = self.printer.set_line_spacing(0) + ''.join(top)
		bottom = ''.join(bottom)

		# apply them to content
		lines = self.component.get_lines(width - 2)
		lines = [left + line.ljust(width - 2) + right for line in lines]
		lines.insert(0, top)
		lines.append(bottom)

		return lines

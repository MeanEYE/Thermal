

class Report:
	"""
	This class is the main container for all the printable components
	from this module. Idea is to create a report by providing active connection.
	Then pack all the printable components into specific report. Program
	can then modify data and simply call print.

	Params:
		connection - Any sort of serial connection, be it bluetooth, serial, network, file;
		dots_per_line - From printer's specification, number of dots per each line;
	"""

	def __init__(self, printer):
		self.printer = printer
		self.components = []

	def add(self, component):
		"""Add printable component to the stack."""
		self.components.append(component)
		component.set_printer(self.printer)

	def print(self, cut_after=False, cut_partial=True):
		"""Print packed components using configured connection and printer."""
		self.printer.reset()
		for component in self.components:
			component.on_printer_reset()

		# alignment and line spacing are printer modes which would otherwise
		# leak from one component into the next, so each component starts
		# from defaults; this must be at the beginning of a line to take effect
		reset_modes = self.printer.set_alignment(0) + self.printer.set_default_line_spacing()
		reset_modes = reset_modes.encode('latin1')

		# go through each component and get lines for printing
		buffer = []
		carry = b''
		width = self.printer.get_width()
		for component in self.components:
			lines = component.get_lines(width)
			if not lines:
				continue

			lines = [line if isinstance(line, bytes) else line.encode('latin1') for line in lines]

			# command only components are carried to the start of next line
			if not component.feeds_line:
				carry += b''.join(lines)
				continue

			lines[0] = reset_modes + carry + lines[0]
			carry = b''
			buffer.extend(lines)

		if carry:
			buffer.append(carry)

		self.printer.print(b'\x0A'.join(buffer))
		self.printer.line_feed()

		# feed to cutting position and cut paper if requested
		if cut_after and self.printer.supports_cutting:
			self.printer.cut_paper(cut_partial, feed=self.printer.cut_feed_units)

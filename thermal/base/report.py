

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

		# go through each component and get lines for printing
		buffer = []
		width = self.printer.get_width()
		for component in self.components:
			lines = component.get_lines(width)

			for line in lines:
				if isinstance(line, bytes):
					buffer.append(line)
				else:
					buffer.append(line.encode('latin1'))

		self.printer.print(b'\x0A'.join(buffer))
		self.printer.line_feed()

		# cut paper if requested
		if cut_after and self.printer.supports_cutting:
			self.printer.line_feed_in_units(self.printer.offset_units)
			self.printer.cut_paper(cut_partial)



class Component:
	"""Base component class which is inherited and then added to
	the report to be printed upon request."""

	def __init__(self):
		self.printer = None

	def set_printer(self, printer):
		"""Set printer to be used for various calculations."""
		self.printer = printer

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		raise NotImplemented()

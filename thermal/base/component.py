

class Component:
	"""Base component class which is inherited and then added to
	the report to be printed upon request."""

	# components which only emit printer commands and no printable
	# content set this to False; report then puts their output at the
	# beginning of the next component's first line instead of feeding
	# a line after them
	feeds_line = True

	def __init__(self):
		self.printer = None

	def set_printer(self, printer):
		"""Set printer to be used for various calculations."""
		self.printer = printer

	def on_printer_reset(self):
		"""Called after printer is initialized and before printing. Components
		keeping state on the printer side (uploaded images) must drop it here."""
		pass

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		raise NotImplemented()

from ..base.component import Component


class Spacer(Component):
	"""Prints given number of empty lines."""

	def __init__(self, lines=1):
		Component.__init__(self)
		self.lines = lines

	def set_lines(self, lines):
		"""Set number of empty lines."""
		self.lines = lines

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		return [''] * self.lines

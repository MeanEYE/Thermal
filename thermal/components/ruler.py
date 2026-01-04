from ..base.component import Component


class Ruler(Component):
	"""Horizontal ruler component renders a single or double-line
	to full horizontal width."""

	def __init__(self, double=False):
		self.double = double

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		char = '\xCD' if self.double else '\xC4'
		return [(char * width),]

from ..base.component import Component


class Flip(Component):
	"""Splitter component which toggles upside-down printing for all
	components that follow it. Add another one to toggle back. Without
	argument mode is toggled, `True` or `False` sets it explicitly.

	Printer rotates each line by 180 degrees but keeps the order of
	lines, so a flipped block reads bottom-up once paper is turned
	around. Mode is turned off at the start of each report print.
	"""
	feeds_line = False

	def __init__(self, upside_down=None):
		Component.__init__(self)
		self.upside_down = upside_down

	def set_upside_down(self, upside_down=None):
		"""Set mode to `True`, `False` or `None` to toggle."""
		self.upside_down = upside_down

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		if self.upside_down is None:
			enabled = not self.printer.upside_down
		else:
			enabled = self.upside_down

		return [self.printer.set_upside_down(enabled),]

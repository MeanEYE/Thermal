
from ..base.printer import Printer


class EpsonPrinter(Printer):
	"""Generic EPSON 80mm printer."""

	# printer specification
	dots_per_line = 512
	paper_width = 80
	supports_cutting = True
	default_code_page = 0
	offset_lines = 3  # number of lines to feed before print is fully visible
	offset_units = 350

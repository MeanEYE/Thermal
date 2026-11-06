
from ..base.printer import Printer


class EpsonPrinter(Printer):
	"""Generic EPSON 80mm printer."""

	# printer specification
	print_area = 512
	supports_cutting = True
	cut_feed_units = 0
	default_code_page = 0
	legacy_graphics = False

	def __init__(self, connection):
		Printer.__init__(self, connection)
		self.narrow = False

	def __apply_print_area(self):
		"""docstring for __set_print_area"""
		self.print_area = 360 if self.narrow else 512
		low, high = chr(self.print_area % 256), chr(self.print_area // 256)
		self.connection.write(f'{self.GS}W{low}{high}')

	def connect(self):
		"""Connect printer."""
		Printer.connect(self)
		self.__apply_print_area()

	def reset(self):
		"""Reset printer to default configuration."""
		Printer.reset(self)
		self.__apply_print_area()

	def set_narrow(self, narrow=True):
		"""Epson printers have adapters to use 58mm as well as 80mm. This
		method tells printer to use narrow paper and align things based on
		that."""
		self.narrow = narrow


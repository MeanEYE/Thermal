import math
import textwrap

from functools import reduce

from ..base.component import Component
from ..components import Border


class TableError(Exception): pass


class Table(Component):
	"""Object which arranges and prints data in table like manner. After table is
	created user will have to add `Column` objects to it and only then populate data."""

	def __init__(self, columns=None):
		self.columns = columns
		self.data = []
		self.footer = None
		self.border = (2, 2, 2, 2)
		self.code_page = None

		# table options
		self.print_titles = True
		self.print_border = True
		self.print_cell_lines = True

	def set_printer(self, printer):
		"""Set printer to be used for various calculations."""
		Component.set_printer(self, printer)
		if self.footer:
			self.footer.set_printer(printer)

		for column in self.columns:
			if not isinstance(column.title, Component):
				continue
			column.title.set_printer(printer)

	def on_printer_reset(self):
		"""Forward printer reset to footer and component titles."""
		if self.footer:
			self.footer.on_printer_reset()

		for column in self.columns:
			if isinstance(column.title, Component):
				column.title.on_printer_reset()

	def set_print_titles(self, print_titles=True):
		"""Configure printing column titles."""
		self.print_titles = print_titles

	def set_print_border(self, print_border=True):
		"""Configure printing table border."""
		self.print_border = print_border

	def set_print_cell_lines(self, print_cell_lines):
		"""Configure printing cell lines."""
		self.print_cell_lines = print_cell_lines

	def set_code_page(self, code_page):
		"""Set code page for cell values and column titles. Borders and
		cell lines stay in printer's default page so box characters
		print correctly with any page."""
		self.code_page = code_page

	def set_footer(self, footer):
		"""Sets footer component which can be used to print summaries
		and similar information."""
		if not isinstance(footer, Component):
			raise TableError('Instance of component is needed.')
		self.footer = footer

	def add_column(self, column):
		"""Add column to the table."""
		if isinstance(column, Column):
			self.columns.append(column)

	def add_row(self, row):
		"""Add tuple of values. Number of values must be the same as number of columns."""
		if len(row) != len(self.columns):
			raise TableError('Number of data points differs from number of columns in the table.')

		if not isinstance(row, tuple):
			raise TableError('We require data points in tuples.')

		self.data.append(row)

	def clear_table(self):
		"""Remove all data from the table."""
		self.data = []

	def get_lines(self, width):
		"""Return list of lines to be printed."""
		result = []

		def subtract(x, y):
			if x is None: return y
			if y is None: return x
			return x - y

		# code page switches around cell content, empty if not requested
		if self.code_page is not None:
			page_on = self.printer.set_code_page(self.code_page)
			page_off = self.printer.set_code_page(self.printer.default_code_page)
		else:
			page_on = page_off = ''

		def prepare_cell(width, value, border):
			value = textwrap.wrap(
					str(value), width=width, expand_tabs=True, replace_whitespace=True,
					fix_sentence_endings=False, break_long_words=True, drop_whitespace=True,
					break_on_hyphens=True, tabsize=0, max_lines=None, placeholder='…'
					)

			output = '{:<' + str(width) + '}'
			return tuple(page_on + output.format(v) + page_off + border for v in value)

		# prepare column widths
		initial_width = width - (len(self.columns) - 1)
		if self.print_border:
			initial_width -= 2

		widths = tuple(column.get_width() for column in self.columns)
		remaining = reduce(subtract, (initial_width, ) + widths)
		default_count = len(tuple(filter(lambda x: x is None, widths)))
		default_width = math.floor(remaining / default_count) if default_count > 0 else 0

		# resolve flexible columns, last one takes the remainder so rows
		# are exactly as wide as border lines
		flexible = [index for index, column_width in enumerate(widths) if column_width is None]
		widths = [column_width or default_width for column_width in widths]
		if flexible:
			widths[flexible[-1]] += remaining - default_width * default_count

		# prepare horizontal lines
		top_border, right_border, bottom_border, left_border = self.border
		top = list(Border.h_chars[top_border] * width)
		header = list(Border.h_chars[top_border] * width)
		footer = list(Border.h_chars[bottom_border] * width)
		bottom = list(Border.h_chars[bottom_border] * width)
		right = Border.v_chars[right_border]
		left = Border.v_chars[left_border]

		if self.print_border:
			top[0] = Border.corners['tl'][f'{top_border}{left_border}']
			top[-1] = Border.corners['tr'][f'{top_border}{right_border}']
			bottom[0] = Border.corners['bl'][f'{bottom_border}{left_border}']
			bottom[-1] = Border.corners['br'][f'{bottom_border}{right_border}']
			header[0] = Border.footer_cell['l'][top_border]
			header[-1] = Border.footer_cell['r'][top_border]
			footer[0] = Border.footer_cell['l'][bottom_border]
			footer[-1] = Border.footer_cell['r'][bottom_border]

		pos = 0
		columns = ''
		if self.print_border:
			pos = 1
			columns += Border.v_chars[left_border]

		for index, column in enumerate(self.columns):
			cw = widths[index]
			pos += cw

			# update columns row
			columns += f'{self.printer.ESC}E1' + page_on + column.get_title(cw) + page_off + f'{self.printer.ESC}E0'

			# update characters
			if index == len(widths) - 1:
				if self.print_border:
					columns += Border.v_chars[right_border]
				break
			else:
				columns += Border.v_chars[self.print_cell_lines]

			if self.print_cell_lines:
				top[pos] = Border.top_cell[top_border]
				header[pos] = Border.middle_cell[top_border]
				footer[pos] = Border.bottom_cell[bottom_border]
				if not self.footer:
					bottom[pos] = Border.bottom_cell[bottom_border]

			pos += 1

		# prepare header
		if self.print_border:
			result.append(''.join(top))

		if self.print_titles:
			result.append(''.join(columns))
			result.append(''.join(header))

		# prepare data for printing
		for row in self.data:
			processed_row = []

			# wrap all the column values to column widths
			for index, column in enumerate(widths):
				cw = widths[index]
				if index < len(self.columns) - 1:
					end_char = Border.v_chars[self.print_cell_lines]
				elif self.print_border:
					end_char = Border.v_chars[right_border]
				else:
					end_char = ''
				processed_row.append(prepare_cell(cw, row[index], end_char))

			# find values with most lines and populate others with empty lines
			max_lines = max(map(lambda r: len(r), processed_row))
			for index, value_lines in enumerate(processed_row):
				missing_lines = max_lines - len(value_lines)

				if index < len(self.columns) - 1:
					end_char = Border.v_chars[self.print_cell_lines]
				else:
					end_char = Border.v_chars[right_border]

				empty_line = ' ' * widths[index] + end_char
				processed_row[index] = value_lines + ((empty_line,) * missing_lines)

			final_rows = zip(*processed_row)
			for r in final_rows:
				line = ''.join(r)
				if self.print_border: line = Border.v_chars[right_border] + line
				result.append(line)

		# prepare footer
		if self.footer:
			result.append(''.join(footer))
			lines = self.footer.get_lines(width - 2)
			if self.print_border:
				lines = [left + line.ljust(width - 2) + right for line in lines]
			else:
				lines = [line.ljust(width) for line in lines]
			result.extend(lines)

		if self.print_border:
			result.append(''.join(bottom))

		# set line spacing so lines can meet
		result[0] = self.printer.set_line_spacing(0) + result[0]
		return result


class Column:
	"""Object representing columns in a table. It's used to organize data and
	format them for printing."""

	def __init__(self, title=None, width=None):
		self.title = title
		self.width = width

	def set_title(self, title):
		"""Set string or component as title."""
		self.title = title

	def get_title(self, width):
		"""Generate title and constrain it to specified width."""
		if isinstance(self.title, Component):
			lines = self.title.get_lines(width)
			title = ''.join(lines)
		else:
			title = self.title

		output = '{:<' + str(width) + '}'
		return output.format(title)

	def set_width(self, width):
		"""Set width in characters or reset it with `None`."""
		self.width = width

	def get_width(self):
		"""Return width of the column."""
		return self.width

	def format_data(self, data):
		"""Format data and return string to be printed."""
		pass

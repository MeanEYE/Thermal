#!/usr/bin/env python
"""
Comprehensive example which uses every component and most of the markup
tags. It also demonstrates the main idea behind the module: report
structure is built once, then data is changed and report printed again.

Swap the connection below for `DebugConnection()` to see the generated
ESC/POS stream in the terminal instead of printing.
"""

import os
import random

from thermal.printers import EpsonPrinter
from thermal.base import Report
from thermal.connections import BluetoothConnection, UsbConnection, DebugConnection
from thermal.components import Text, Ruler, Border, Table, Column, BarCode, MatrixCode, Image, Flip


# connection = BluetoothConnection('66:12:B5:6A:99:21', 1)
# connection = DebugConnection()

connection = UsbConnection(0x04b8, 0x0202)
printer = EpsonPrinter(connection)
report = Report(printer)


# --- header -------------------------------------------------------------

# logo is loaded from monochrome PBM file (both P1 and P4 are supported),
# uploaded once per print and printed centered at double size
logo = Image()
logo.load_from_pbm(os.path.join(os.path.dirname(__file__), 'image.input.pbm'))
logo.set_alignment(1)
logo.set_scale(2, 2)
report.add(logo)

# size is zero based, `[size 1,1]` is double width and height
report.add(Text('[align c][size 1,1][em]Thermal Demo[/em][/size]'))
report.add(Text('[align c][font 1]Comprehensive component test[font 0]'))
report.add(Ruler(double=True))

# order number and date are placeholders updated before each print
report.add(order_line := Text('Order: [em]#{}[/em]'))
report.add(Ruler())


# --- text formatting ----------------------------------------------------

report.add(Text(
	'Inline markup: [em]emphasized[/em], [u]underlined[/u], '
	'[u2]double underlined[/u], [st]double strike[/st] and '
	'[inv]inverted[/inv]. Long text is wrapped to printer width '
	'automatically so paragraphs just work.'
	))
report.add(Text('[size 1,0]Double width[/size] and [size 0,1]double height[/size]'))
report.add(Text('[align r]Right aligned line'))
report.add(Text('[align c]Centered line'))

# text in different code page, 16 is Windows-1252 on Epson printers
report.add(encoded := Text('Code page: caf\xE9 cr\xE8me br\xFBl\xE9e'))
encoded.set_code_page(16)

# tabs advance to the next stop, by default every 8 characters
report.add(Text('Tabs:[tab]one[tab]two[tab]three'))

# custom tab stops give column layout without padding, stops are
# positions in characters from the left and stay set until next
# change or report print
report.add(tabbed := Text('Code[tab]Description[tab]Qty'))
tabbed.set_tab_stops([6, 30])
report.add(Text('A1[tab]Widget[tab]2'))
report.add(Text('B22[tab]Gadget with a long name[tab]10'))


# --- borders ------------------------------------------------------------

# border is (top, right, bottom, left) where 0 is none, 1 single, 2 double
report.add(Border(Text('Single line border around wrapped text component.')))
report.add(Border(Text('Double border with single sides.'), border=(2, 1, 2, 1)))
report.add(Border(Border(Text('Nested borders work too.')), border=(2, 2, 2, 2)))


# --- table --------------------------------------------------------------

# columns without width share whatever is left after fixed ones
table = Table([
	Column('#', width=2),
	Column('Item'),
	Column('Qty', width=3),
	Column('Price', width=7),
	])
table.set_footer(total_line := Text('Total: {:.2f}'))
report.add(table)

# same table style without border and cell lines
plain_table = Table([Column('Code', width=8), Column('Description')])
plain_table.set_print_border(False)
plain_table.set_print_cell_lines(False)
plain_table.add_row(('A-100', 'Plain table, no border and no cell lines'))
plain_table.add_row(('B-200', 'Titles are still emphasized'))
report.add(plain_table)


# --- codes --------------------------------------------------------------

# CODE39 bar code with human readable text printed below in font B
barcode = BarCode('THERMAL', BarCode.CODE39)
barcode.set_height(60)
barcode.set_width(2)
barcode.set_text_position(BarCode.TEXT_BELOW)
barcode.set_text_font(BarCode.FONT_B)
report.add(barcode)

# QR code with error correction level and module size in dots
qr = MatrixCode('https://gitlab.com/MeanEYE/Thermal', MatrixCode.QR_CODE)
qr.set_error_correction(MatrixCode.ERROR_M)
qr.set_module_size(5)
report.add(qr)

# Data Matrix, size is picked by the printer unless set
matrix = MatrixCode('Thermal', MatrixCode.DATA_MATRIX)
matrix.set_module_size(4)
matrix.set_align(MatrixCode.ALIGN_RIGHT)
report.add(matrix)


# --- inline image and footer --------------------------------------------

# already uploaded image can be referenced from text by its id, with
# optional scale; text is broken around it as printers only print
# graphics at the beginning of a line
report.add(Text(f'Reference to logo by id [img {logo.image_id} 1,1] and text continues after it.'))
report.add(Ruler(double=True))
report.add(Text('[align c][em]Thank you![/em]'))

# everything after Flip is printed upside down until the next Flip,
# useful for a part of receipt facing the other way; printer rotates
# lines but keeps their order so they are added here bottom-up
report.add(Flip())
report.add(Text('[align c]Merchant copy'))
report.add(Ruler())
report.add(Text('[align c][em]Thermal Demo[/em]'))


# --- data and printing --------------------------------------------------

ITEMS = ('Apples', 'Oranges', 'Melons', 'Grapes', 'Peaches', 'Cherries', 'Strawberries', 'Mangos')

def populate(order_number):
	"""Fill variable parts of the report with fresh data."""
	order_line.set_text(f'Order: [em]#{order_number}[/em]')

	total = 0
	table.clear_table()
	for index in range(random.randint(3, 6)):
		quantity = random.randint(1, 5)
		price = random.randint(10, 500) / 10
		table.add_row((index + 1, random.choice(ITEMS), quantity, f'{price:.2f}'))
		total += quantity * price

	total_line.set_text(f'Total: {total:.2f}')


printer.connect()

# print two receipts from the same report, structure doesn't change
# while data does; paper is cut after each one
for order_number in (1001, 1002):
	populate(order_number)
	report.print(cut_after=True)

printer.disconnect()

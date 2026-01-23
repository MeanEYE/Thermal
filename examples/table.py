import random

from thermal.printers import EpsonPrinter
from thermal.base import Printer, Report
from thermal.connections import BluetoothConnection, UsbConnection, DebugConnection
from thermal.components import Text, Ruler, Border, MatrixCode, Table, Column


# connection = BluetoothConnection('66:12:B5:6A:99:21', 1)
connection = UsbConnection(0x04b8, 0x0202)
# connection = DebugConnection()

printer = EpsonPrinter(connection)
report = Report(printer)

# create header
report.add(Text('[size 1,1][align c][inv]Table Test[/inv][/size]'))
report.add(Text(
	'[align l]This is a simple test of table capability. Bellow '
	'is a table of randomly generated values and randomly picked '
	'items.'
	))

# create table and configure it
table = Table((
	Column('#', width=2),
	Column('Item'),
	Column('Amt', 3),
	Column('Price', width=5)
	))
table.set_footer(footer := Text('Total: {}'))
report.add(table)

# add data to the table
total = 0
fruits = ('Apples', 'Oranges', 'Mellons', 'Grapes', 'Peaches', 'Cherries', 'Strawberries', 'Mangos')
for index in range(5):
	table.add_row((
		index + 1,
		random.choice(fruits),
		count := random.randint(0, 2),
		price := random.randint(1, 1000) / 10
		))
	total += count * price

footer.set_text('Total: {}'.format(total))

# print report and if supported cut page
printer.connect()
report.print()
printer.disconnect()

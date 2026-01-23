from thermal.printers import EpsonPrinter
from thermal.base import Printer, Report
from thermal.connections import BluetoothConnection, UsbConnection, DebugConnection
from thermal.components import Text, Ruler, Border, MatrixCode


# connection = BluetoothConnection('66:12:B5:6A:99:21', 1)
# connection = DebugConnection()

connection = UsbConnection(0x04b8, 0x0202)
printer = EpsonPrinter(connection)
report = Report(printer)

# create header
report.add(Text('[size 1,1][align c][inv]Printer Test[/inv][/size]'))
report.add(Text(
	'[align l]This is a [u]complete[/u] long text on a small '
	'printer which should wrap [em]around[/em]!'
	))

# box containing text followed by QR code
report.add(Border(Text('Test another text Test. Actually long text inside of border.'), border=(2, 2, 1, 2)))
report.add(Ruler(double=False))
report.add(MatrixCode('https://gitlab.com/MeanEYE/Thermal'))

# print report and if supported cut page
printer.connect()
report.print(True)
printer.disconnect()

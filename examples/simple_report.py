from ..thermal.base import Printer, Report
from ..thermal.connections import BluetoothConnection
from ..thermal.components import Text, Ruler, Border, MatrixCode


connection = BluetoothConnection('66:12:B5:6A:99:21', 1)
printer = Printer(connection)

report = Report(printer)

# create header
report.add(Text('[size 1,1][align c][inv]Printer Test[/inv][/size]'))
report.add(Text(
	'[align l]This is a [u]complete[/u] long text test on a small '
	'printer which should wrap [em]around[/em]!'
	))

# box containing text followed by QR code
report.add(Border(Text('Test another text Test. Actually long text inside of border.'), border=(2, 2, 1, 2)))
report.add(Ruler(double=False))
report.add(MatrixCode('https://gitlab.com/MeanEYE/Thermal'))

# print report and if supported cut page
report.print(cut_after=True)

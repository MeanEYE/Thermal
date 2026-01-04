import random

from thermal.base import Printer, Report
from thermal.connections import BluetoothConnection, FileConnection
from thermal.components import Text, Ruler, Border, BarCode, MatrixCode


connection = BluetoothConnection('66:12:B5:6A:99:21', 1)
printer = Printer(connection)
report = Report(printer)

report.add(Text('[size 1,1][align c][inv]Printer Test[/inv][/size]'))
report.add(Text(
	'[align l]This is a [u]complete[/u] long text test on a small '
	'printer which should wrap [em]around[/em]!'
	))
report.add(Border(Text('Test another text Test. Actually long text inside of border.'), border=(2, 2, 1, 2)))
report.add(Ruler(True))
report.add(qr := MatrixCode('https://www.scribd.com/document/331367389/58MM-MINI-Portable-Thermal-Printer-Instruction-Manual-20160805'))
qr.set_module_size(4)
report.print(cut_after=True)

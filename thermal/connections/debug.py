import sys

from .connection import Connection


class DebugConnection(Connection):
	"""Debugging connection which just prints output."""

	def __init__(self):
		Connection.__init__(self)
		self.data = b''

	def connect(self):
		"""Connect to specified target connection or raise an exception."""
		pass

	def close(self):
		"""Shutdown file connection and release resources."""
		hex_output = ''
		ascii_output = ''

		lookup = {
				'\x0d': '{CR}', '\x0a': '{LF}', '\x1b': '{ESC}',
				'\x1d': '{GS}', '\x09': '{TAB}',
				}

		RESET = "\033[0m"
		RED = "\033[31m"
		GREEN = "\033[32m"
		YELLOW = "\033[33m"
		BLUE = "\033[34m"
		MAGENTA = "\033[35m"
		CYAN = "\033[36m"
		WHITE = "\033[37m"

		for index, byte in enumerate(self.data, start=1):
			hex_color = BLUE if index % 2 == 0 else CYAN
			hex_output += hex_color + f'{byte:02x}'
			if chr(byte) in lookup:
				ascii_output += GREEN + lookup[chr(byte)] + YELLOW
			else:
				ascii_output += chr(byte) if 32 <= byte <= 126 else '˽'

			if index % 50 == 0:
				print('Hex:     ' + hex_output)
				print('ASCII:   ' + YELLOW + ascii_output + RESET)
				hex_output = ''
				ascii_output = ''

		print('Hex:     ' + hex_output)
		print('ASCII:   ' + YELLOW + ascii_output + RESET)

	def write(self, data):
		"""Write data to socket and wait for it to be sent."""
		self.data += bytearray(data, 'utf-8') if isinstance(data, str) else data

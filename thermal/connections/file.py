import socket

from .connection import Connection, ConnectionError, DisconnectionError, ReadError, WriteError


class FileConnectionError(ConnectionError): pass
class FileDisconnectionError(DisconnectionError): pass
class FileReadError(ReadError): pass
class FileWriteError(WriteError): pass


class FileConnection(Connection):
	"""Connect through device file like /dev/usb/lp3 or similar."""

	def __init__(self, path):
		Connection.__init__(self)
		self.path = path
		self.device = None

	def connect(self):
		"""Connect to specified target connection or raise an exception."""
		try:
			self.device = open(self.path, 'wb')
		except OSError as error:
			raise FileConnectionError(f'Unable to open `{self.path}` for writing: {error}')

	def close(self):
		"""Shutdown file connection and release resources."""
		if self.device:
			self.device.flush()
			self.device.close()
			self.device = None

	def read(self):
		"""Read data from socket."""
		raise NotImplemented()

	def write(self, data):
		"""Write data to socket and wait for it to be sent."""
		assert self.device is not None
		if isinstance(data, str):
			data = data.encode('latin1')
		self.device.write(data)
		self.device.flush()

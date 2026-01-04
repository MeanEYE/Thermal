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
		self.device = open(self.path, 'wb')

		if not self.device is None:
			raise FileConnectionError(f'Unable to open `{self.path}` for writing.')

	def close(self):
		"""Shutdown file connection and release resources."""
		if self.device:
			self.device.flush()
			self.device.close()

	def read(self):
		"""Read data from socket."""
		raise NotImplemented()

	def write(self, data):
		"""Write data to socket and wait for it to be sent."""
		assert self.device is not None
		self.device.write(data)
		self.flush()

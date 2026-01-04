

class ConnectionError(Exception): pass
class DisconnectionError(Exception): pass
class ReadError(Exception): pass
class WriteError(Exception): pass


class Connection:
	"""Generit interface class made for inheriting by others."""

	def __init__(self):
		pass

	@classmethod
	def list_available(self):
		"""List available connections for this type."""
		raise NotImplemented()

	def connect(self):
		"""Connect to specified target connection or raise an exception."""
		raise NotImplemented()

	def close(self):
		"""Shutdown socket connection and release resources."""
		raise NotImplemented()

	def read(self):
		"""Read data from socket."""
		raise NotImplemented()

	def write(self, data):
		"""Write data to socket and wait for it to be sent."""
		raise NotImplemented()

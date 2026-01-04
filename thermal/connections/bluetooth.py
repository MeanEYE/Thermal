import socket
import bluetooth

from .connection import Connection, ConnectionError, DisconnectionError, ReadError, WriteError


class BluetoothConnectionError(ConnectionError): pass
class BluetoothDisconnectionError(DisconnectionError): pass
class BluetoothReadError(ReadError): pass
class BluetoothWriteError(WriteError): pass


class BluetoothConnection(Connection):
	"""Connect through bluetooth using RFCOMM."""

	def __init__(self, address, port=1):
		Connection.__init__(self)
		self.socket = None
		self.address = address
		self.port = port

	@classmethod
	def list_available(self, wait_time=2):
		"""List available Bluetooth devices that have RFCOMM port."""
		result = []
		devices = bluetooth.discover_devices(wait_time)

		# no devices were found
		if not devices:
			return result

		# find suitable services and populate result
		for address in devices:
			services = bluetooth.find_service(address=address)

			# skip devices without service
			if not services:
				continue

			# check if one of the services supports serial
			for service in services:
				if service['host'] == address and service['protocol'] == 'RFCOMM':
					result.append(service)

		return result

	def connect(self):
		"""Try to establish connection to configured address."""
		try:
			self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
			self.socket.connect((self.address, self.port))

		except Exception as error:
			raise BluetoothConnectionError(error)

	def close(self):
		"""Shutdown socket connection and release resources."""
		if self.socket is None:
			return

		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket.close()
		self.socket = None

	def read(self):
		"""Read data from socket."""
		result = ''

		try:
			result = self.socket.recv()
		except:
			raise BluetoothReadError('Connection broken!')

		return result

	def write(self, data):
		"""Write data to socket and wait for it to be sent."""
		total_size_sent = 0

		while total_size_sent < len(data):
			size_sent = self.socket.send(data[total_size_sent:])
			if size_sent == 0:
				raise BluetoothWriteError('Connection broken!')
			total_size_sent += size_sent

		return total_size_sent

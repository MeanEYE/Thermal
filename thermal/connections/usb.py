import usb.core
import usb.util

from .connection import Connection, ConnectionError, DisconnectionError, ReadError, WriteError


class UsbConnectionError(ConnectionError): pass


class UsbConnection(Connection):
	"""Generit interface class made for inheriting by others."""

	def __init__(self, vendor, product, interface=0, input_ep=0x82, output_ep=0x01):
		Connection.__init__(self)
		self.device = None
		self.vendor = vendor
		self.product = product
		self.interface = interface
		self.input_endpoint = input_ep
		self.output_endpoint = output_ep

	@classmethod
	def list_available(self):
		"""List available connections for this type."""
		raise NotImplemented()

	def connect(self):
		"""Connect to specified target connection or raise an exception."""
		self.device = usb.core.find(idVendor=self.vendor, idProduct=self.product)
		if self.device is None:
			raise UsbConnectionError(f'Unable to connect to device {self.vendor}:{self.product}!')

		if self.device.is_kernel_driver_active(0):
			try:
				self.device.detach_kernel_driver(0)
			except usb.core.USBError as e:
				raise UsbConnectionError('Error: {}'.format(str(e)))

		try:
			self.device.set_configuration()
			# self.device.reset()
		except usb.core.USBError as e:
			raise UsbConnectionError('Error: {}'.format(str(e)))

	def close(self):
		"""Shutdown socket connection and release resources."""
		if self.device:
			usb.util.dispose_resources(self.device)

	def read(self):
		"""Read data from socket."""
		raise NotImplemented()

	def write(self, data):
		"""Write data to socket and wait for it to be sent."""
		assert self.device
		self.device.write(self.output_endpoint, data, self.interface)

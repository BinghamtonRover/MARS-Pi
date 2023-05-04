import serial

from network.generated import MarsData

class MarsSerial: 
	def __init__(self, mars, port): 
		self.device = serial.Serial(port, 9600)
		self.mars = mars

	def send(self, data):
		"""Sends the data as-is over Serial"""
		self.device.write(data)

	def get_data(self): 
		"""Returns a MarsData received over Serial"""
		serial_bytes = self.device.read(size=self.device.in_waiting)
		if not serial_bytes: return None
		return MarsData.FromString(serial_bytes)

	def close(self): 
		"""Closes the Serial port to be used again later"""
		self.device.close()

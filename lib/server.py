import time

from network import ProtoSocket
from network.generated import *

DATA_SEND_INTERVAL = 1  # in seconds

class MarsServer(ProtoSocket): 
	def __init__(self, mars): 
		super().__init__(port=8006, device=Device.MARS_SERVER)
		self.mars = mars
		self.status = MarsStatus.PORT_NOT_FOUND
		self.last_send_time = time.time()

	# Overriden from ProtoSocket
	def on_message(self, wrapper): 
		if wrapper.name != "MarsCommand": print("Got an unknown message")
		else: self.mars.serial.send(wrapper.data)

	# Overriden from ProtoSocket
	def on_loop(self): 
		super().on_loop()
		data = self.mars.serial.get_data()
		if data is not None: self.send_message(data)
		# The MarsData fields come from the Teensy, but the status must be set here
		if not self.is_connected(): return
		if (time.time() - self.last_send_time) < DATA_SEND_INTERVAL: return
		message = MarsData(status=self.status)
		self.send_message(message)

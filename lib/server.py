from network import ProtoSocket
from network.generated import Device

class MarsServer(ProtoSocket): 
	def __init__(self, mars): 
		self.mars = mars
		super().__init__(port=8006, device=Device.MARS_SERVER)

	# Overriden from ProtoSocket
	def on_message(self, wrapper): 
		if wrapper.name != "MarsCommand": print("Got an unknown message")
		else: self.mars.serial.send(wrapper.data)

	# Overriden from ProtoSocket
	def on_loop(self): 
		super().on_loop()
		data = self.mars.serial.get_data()
		if data is not None: self.send_message(data)

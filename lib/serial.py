import serial
import google.protobuf
import warnings
import threading

from network import *
from network.generated import *

class MarsSerial: 
	def __init__(self, mars, port): 
		# Do not initialize with the port. Otherwise it will open and throw immediately
		self.device = serial.Serial(None, 9600, timeout=1)
		self.device.port = port
		self.mars = mars
		self.is_connected = False
		self.keep_alive = True

	def send(self, data):
		"""Sends the data as-is over Serial"""
		if not self.is_connected: return
		self.device.write(data)

	def get_data(self): 
		"""Returns a MarsData received over Serial"""
		if not self.is_connected: return None
		if not self.device.in_waiting: return None
		serial_bytes = self.device.read(size=self.device.in_waiting)
		if not serial_bytes: return None
		return MarsData.FromString(serial_bytes)

	def close(self): 
		"""Closes the Serial port to be used again later"""
		self.device.close()
		self.keep_alive = False

	def await_open_port(self): 
		print(f"Opening port {self.device.port}...", end="", flush=True)
		while True: 
			print(".", end="", flush=True)
			try: self.device.open()
			except serial.SerialException as error: 
				if str(error).startswith("could not open port"): time.sleep(1)
				else: raise error from None
			else: break
		print(" Done!", flush=True)

	def parse_protobuf(self, data): 
		if data is None: return None
		with warnings.catch_warnings():
			warnings.simplefilter('ignore')
			try: 
				result = Connect.FromString(data)
				if not result.IsInitialized(): return None
				return result
			except google.protobuf.message.DecodeError: 
				return None

	def await_handshake(self):
		# The firmware expects a handshake from the dashboard, so we have to play pretend
		handshake = Connect(sender=Device.DASHBOARD, receiver=Device.FIRMWARE)
		print("Sending handshake...", end="", flush=True)

		while True: 
			time.sleep(0.5)
			self.send(handshake.SerializeToString())
			print(".", end="", flush=True)
			response_bytes = self.device.read(size=self.device.in_waiting)[-4:]
			if not response_bytes: continue
			response = self.parse_protobuf(response_bytes)
			if response is None: continue
			if response.sender == Device.MARS: break
			else: 
				print(f"\nFailed handshake: {Device.Name(response.sender)} => {Device.Name(response.receiver)}")
				time.sleep(0.5)
				self.mars.server.status = MarsStatus.FAILED_HANDSHAKE
				self.send_disconnect()
		print(" Done!", flush=True)

	def connect(self): 
		print("Connecting to the Mars subsystem...")
		self.mars.server.status = MarsStatus.PORT_NOT_FOUND
		while not self.is_connected: 
			try: 
				self.device.close()
				self.await_open_port()
				self.mars.server.status = MarsStatus.TEENSY_UNRESPONSIVE
				self.send_disconnect()
				self.await_handshake()
				self.mars.server.status = MarsStatus.TEENSY_CONNECTED
				self.is_connected = True
			except serial.SerialException as error:
				if str(error).startswith("WriteFile failed"): 
					print("\nThe port was suddenly disconnected")
					continue
				else: 
					raise error from None

	def send_disconnect(self): 
		# The Teensy might already be connected to some device. This will send a reset command.
		# We can't use the Disconnect message because it can be interpreted as any Protobuf message
		self.send([0, 0, 0, 0])
		response = self.device.read(size=4)
		if response and all(x == 1 for x in response): 
			print("The Teensy has been reset")

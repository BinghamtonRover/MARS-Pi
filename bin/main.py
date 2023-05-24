from network import *
from lib.server import MarsServer
from lib.serial import MarsSerial

SERIAL_PORT = "/dev/ttyACM0"

class Mars:
	def __init__(self): 
		self.server = MarsServer(self)
		self.serial = MarsSerial(self, SERIAL_PORT)

	def close(self):
		self.server.close()
		self.serial.close()

if __name__ == "__main__": 
	mars = Mars()
	thread = ServerThread(mars.server)
	ServerThread.startThreads([thread])

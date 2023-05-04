from lib.server import MarsServer
from lib.serial import MarsSerial

SERIAL_PORT = None

class Mars:
	def __init__(self): 
		self.server = MarsServer(self)
		self.serial = MarsSerial(self, SERIAL_PORT)

	def close(self):
		self.server.close()
		self.serial.close()

if __name__ == "__main__": 
	mars = Mars()
	try: 
		while True: 
			try: mars.server.listen()
			except KeyboardInterrupt: break
			except OSError as error: 
				if error.errno == 10054: continue
				else: raise error
	finally: mars.close()


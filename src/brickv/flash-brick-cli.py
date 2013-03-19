import argparse
from samba import SAMBA, SAMBAException, get_serial_ports
from serial import SerialException

class CLIProgress:
	def __init__(self):
		self.message = ""
		self.value = 0
		self.max = 0
	
	def print_progress(self):
		print("\r{0}: {1:>3} %".format(self.message, int(100.0 * self.value / self.max))),
	
	def reset(self, title, max):
		print("")
		self.message = title
		self.value = 0
		self.max = max
		self.print_progress()
			
	def update(self, value):
		self.value = value
		self.print_progress()
	
	def cancel(self):
		pass
		
	def setMaximum(self, value):
		self.max = value
		self.print_progress()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Used to flash firmware onto a brick')
	parser.add_argument("-p", "--port", dest = "port", required = True, type=str, help = "the name of the serial-port the brick is connected to")
	parser.add_argument("-f", "--file", dest = "file", required = True, type=str, help = "The path to the firmware-file")
	
	args = parser.parse_args()
	
	firmware = None
	try:
		with open(args.file, "rb") as firmware_file:
			firmware = firmware_file.read()
	except IOError as e:
		print("(Error) Could not read file: {0}".format(e.strerror))
		exit(-1)
	
	try:
		samba = SAMBA(args.port, CLIProgress())
		samba.flash(firmware, None, False)
	except SerialException as e:
		print("(Error) {0}".format(e))
		exit(-1)
	except SAMBAException as e:
		print('(Error) Could not connect to Brick: {0}'.format(e))
		exit(-1)
	exit(0)

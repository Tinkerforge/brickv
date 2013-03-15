import argparse
from samba import SAMBA, SAMBAException, get_serial_ports

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Used to flash firmware onto a brick')
	parser.add_argument("-p", "--port", dest = "port", required = True, type=str, help = "the name of the serial-port the brick is connected to")
	parser.add_argument("-f", "--file", dest = "file", required = True, type=str, help = "The path to the firmware-file")
	
	args = parser.parse_args()
	
	firmware = None
	with open(args.file, "rb") as firmware_file:
		firmware = firmware_file.read()
	
	samba = SAMBA(args.port)
	samba.flash(firmware, None, None)
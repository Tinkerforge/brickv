#!/usr/bin/env python

try:
	import argparse
except ImportError:
	print('Error: Requiring Python argparse module')
	exit(1)

try:
	from serial import Serial, SerialException
except ImportError:
	print('Error: Requiring Python serial module')
	exit(2)

from samba import SAMBA, SAMBAException

class Progress:
	def __init__(self):
		self.message = ''
		self.value = 0
		self.maximum = 0
		self.first_reset = True

	def print_progress(self):
		print('\r{0}: {1:>3} %'.format(self.message, int(100.0 * self.value / self.maximum))),

	def reset(self, title, maximum):
		if not self.first_reset:
			print('')
		else:
			self.first_reset = False

		self.message = title
		self.value = 0
		self.maximum = maximum
		self.print_progress()

	def update(self, value):
		self.value = value
		self.print_progress()

	def cancel(self):
		pass

	def setMaximum(self, value):
		self.maximum = value
		self.print_progress()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Used to flash firmwares onto a Tinkerforge Bricks')
	parser.add_argument('-p', '--port', dest='port', required=True, type=str, help='name of the serial port the Brick is connected to, typically /dev/ttyUSB0 or /dev/ttyACM0')
	parser.add_argument('-f', '--file', dest='file', required=True, type=str, help='path to the firmware file')

	args = parser.parse_args()
	firmware = None

	try:
		with open(args.file, 'rb') as firmware_file:
			firmware = firmware_file.read()
	except IOError as e:
		print('Error: Could not read firmware: {0}'.format(e.strerror))
		exit(3)

	try:
		samba = SAMBA(args.port, Progress())
		samba.flash(firmware, None, False)
	except SerialException as e:
		print('Error: {0}'.format(e))
		exit(4)
	except SAMBAException as e:
		print('Error: Could not connect to brick: {0}'.format(e))
		exit(5)
	finally:
		samba = None

	print('')
	print('Brick successfully flashed')
	exit(0)

import time
import serial

class sconsole:
	def __init__(self):
		self.serial = serial.Serial(
			port='/dev/ttyS0',
			baudrate=9600,
			parity=serial.PARITY_ODD,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.SEVENBITS
		)
		self.serial.open()
		self.serial.isOpen()

	def __del__(self):
		self.serial.close()

	def read(self):
		while self.serial.inWaiting() > 0:
			return self.serial.read(self.serial.inWaiting())
		return None

	def updateConsole(self, console):
		b = console.get_buffer()
		cont = self.read()
		if cont != None and cont.isalnum():
			print "str:%s|" % cont
			b.insert(b.get_end_iter(), cont)
			console.scroll_mark_onscreen(b.get_insert())
		return True

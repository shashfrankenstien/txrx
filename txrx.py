#!/usr/bin/python
__author__ = "Shashank Gopikrishna"
__version__ = "0.0.1"
__email__ = "shashank.gopikrishna@gmail.com"

import time
import threading
import cpuinfo
from sleepTest import sleeperror

# Check if device is a respberry pi
if cpuinfo.this_is_a_pi():
	import RPi.GPIO as gpio
	tx = 37
	rx = 40

# Check if device is a C.H.I.P
elif cpuinfo.this_is_a_chip():
	import CHIP_IO.GPIO as gpio
	gpio.cleanup()
	tx = 'CSID0'
	rx = 'CSID1'

# Neither -> quit()
else:
	print 'Device not supported'
	quit()



def rand_id_gen(size=64):
	"""Generates salt for password encryption"""
	alph = str(string.lowercase+string.digits)*2
	return str(''.join(random.sample(alph, size)))




class TXRXProtocol(object):
	_serr = sleeperror()
	# short_delay = 0.001
	# half_pulse = short_delay*0.27
	# short_delay = 0.0004-_serr
	# half_pulse = short_delay*0.222
	short_delay = 0.0006-_serr
	half_pulse = short_delay*0.214
	long_delay = short_delay*2-_serr
	stabilizer_byte = '0000'
	pad_byte = '10011111'
	trail_byte = '010'

	def _byte_contain(self, byte):
		return self.stabilizer_byte+self.pad_byte+byte+self.trail_byte

	def _find_one_message(self, string, mlength=8):
		msg = None
		remainder = string
		try:
			mloc = string.index(self.pad_byte)+len(self.pad_byte)
			if len(string[mloc:]) >= mlength+len(self.trail_byte):
				msg_t = string[mloc:mloc+mlength]
				tb = string[mloc+mlength:mloc+mlength+len(self.trail_byte)]
				remainder = string[mloc+mlength:]
				if tb[0] == self.trail_byte[0]:
					msg = msg_t
		except ValueError:
			pass
		except Exception as e:
			if self.debug: print str(e)
		return msg, remainder
	

class RFDriver(TXRXProtocol):
	'''
	Exposes low level RF transmission and reception methods.
	debug = 1 displays received character

	RF = RFDriver(tx_pin=tx, rx_pin=rx, debug=1)
	RF.listen()
	RF.transmit_binary('10101010')
	time.sleep(4)
	RF.terminate()
	'''


	def __init__(self, tx_pin, rx_pin, debug=0):
		self.TX = tx_pin
		self.RX = rx_pin
		self.debug = debug
		self.receiving = False
		self.receiveThread = None
		self.processThread = None
		self.lock = threading.Lock()
		self._buffer = ''
		self._subscriptions = [self._defaultSubscription] if self.debug else []
		self._setup_gpio()

	def _setup_gpio(self):
		try:
			if cpuinfo.this_is_a_pi(): gpio.setmode(gpio.BOARD)
			gpio.setwarnings(False)
			gpio.setup(self.TX, gpio.OUT, initial=gpio.LOW)
			gpio.setup(self.RX, gpio.IN)#, pull_up_down=gpio.PUD_DOWN)
		except Exception as e:
			print str(e)

	def _defaultSubscription(self, bn):
		print 'Message Received->', str(bn)


	def transmit_binary(self, code):
		bn_encl = self._byte_contain(code)
		if cpuinfo.this_is_a_pi(): gpio.setmode(gpio.BOARD)
		for i in bn_encl:
			if i == '1':
				gpio.output(self.TX, gpio.HIGH)
				time.sleep(self.short_delay)
				gpio.output(self.TX, gpio.LOW)
				time.sleep(self.long_delay)
			elif i == '0':
				gpio.output(self.TX, gpio.HIGH)
				time.sleep(self.long_delay)
				gpio.output(self.TX, gpio.LOW)
				time.sleep(self.short_delay)
			else:
				continue
		gpio.output(self.TX, 0)


	def _fetch_from_buffer(self):
		self.lock.acquire()
		m = self._buffer
		self._buffer = ''
		self.lock.release()
		return str(m)

	def _receiver(self):
		high_count = 0
		print '**Started RF receiving thread'
		while self.receiving:
			if cpuinfo.this_is_a_pi(): 
				gpio.setmode(gpio.BOARD)
			gpio.setup(self.RX, gpio.IN, pull_up_down=gpio.PUD_DOWN)
			if gpio.input(self.RX):
				high_count+=1
			else: 
				if high_count > 1:
					if self.debug==3: print 'high:',high_count, '\t0' if high_count <= 4 else '\t1'
					if cpuinfo.this_is_a_pi(): 
						self._buffer += '0' if high_count < 4 else '1'
					else:
						self._buffer += '1' if high_count < 4 else '0'
				high_count=0
			time.sleep(self.half_pulse)
		print '**Ended RF receiving thread'
		gpio.cleanup()


	def _processor(self):
		string=''
		print '**Started RF processing thread'
		while self.receiving or len(self._buffer):
			string += self._fetch_from_buffer()
			if len(string):
				msg, remainder = self._find_one_message(string)
				if msg:
					if self.debug: print 'message found {} in {}'.format(msg, string)
					for func in self._subscriptions:
						try:
							func(msg)
							# print 'LastChar = ', string[s+8]
						except Exception as e: 
							if self.debug==2: print str(e)
				string = remainder
			# if len(string)<16: time.sleep(0.1)
			time.sleep(0.02)
		print '**Ended RF processing thread'


	def listen(self):
		time.sleep(0.5)
		self.receiving = True
		self.receiveThread = threading.Thread(target=self._receiver)
		self.receiveThread.start()
		self.processThread = threading.Thread(target=self._processor)
		self.processThread.start()
		time.sleep(0.5)
		return True

	def subscribe_binary(self, func):
		self._subscriptions.append(func)
		return True

	def terminate(self):
		self.receiving = False
		self.receiveThread.join()
		self.processThread.join()
		gpio.cleanup()
		return True
		




class RFMessageProtocol(object):
	__config__ = 'MASTER'
	__id__ = 'M'
	PING='Pi'
	PONG='Po'

	MSG_CONTAINER = ('<','>')

	def _proto_contain(self, msg):
		return self.MSG_CONTAINER[0]+str(msg)+self.MSG_CONTAINER[1]

	def _proto_ping_to(self, dest):
		'''src|dest|message'''
		return '{}|{}|{}'.format(self.__id__, dest, self.PING)

	def _proto_pong_to(self, dest):
		'''src|dest|message'''
		return '{}|{}|{}'.format(self.__id__, dest, self.PONG)

	def _proto_ping_sniffer(self, msg):
		try:
			s,d,m = msg.split('|')
			if d==self.__id__ and (m == self.PING or m == self.PONG):
				return s,d,m
			else:
				return False
		except Exception as e:
			# print str(e)
			return False

				  


class RFMessenger(RFDriver, RFMessageProtocol):
	'''
	Higher level access to transmission and message handling.
	
	###Usage
	def demo_printer(msg):
		print 'Received ->', str(msg)
		
	RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=1)
	RF.subscribe(demo_printer)
	RF.listen()
	
	if RF.ping(dest=RF.__id__, n=3, silent=False):
		RF.send('3way h-shake')
	time.sleep(3)
	RF.terminate()
	'''

	def __init__(self, tx_pin, rx_pin, debug=0):
		super(RFMessenger, self).__init__(tx_pin, rx_pin, debug)
		self._temp_msg = ''
		self._ping_tracker = {}
		self.subscribe_binary(self._binary_reader)
		self._msg_subscriptions = []

	def to_binary(self, ch):
		'''Converts a character to a binary str repr'''
		b = format(ord(ch), 'b')
		return (8-len(b))*'0'+b


	def to_char(self, bn):
		'''Converts a binary str to a character'''
		if bn: 
			return chr(int(bn[:8], 2))
		else:
			raise ValueError('Binary data not found')


	def transmit_char(self, ch):
		bn = self.to_binary(ch)
		self.transmit_binary(bn)
		if self.debug: print 'Sent->', ch, 'as', bn
		return True


	def send(self, string, n=1, delay=1):
		msg = self._proto_contain(string)
		if self.debug: print 'Sending ->', msg
		for i in xrange(n):
			for ch in msg:
				self.transmit_char(ch)
				time.sleep(0.01)
			if n>1: time.sleep(delay)
		return True


	def ping(self, dest, n=1, double=False, silent=True):
		self._ping_tracker[dest] = ''
		while self._ping_tracker[dest] != self.PONG and n>0:
			self._ping_tracker[dest] = ''
			if not silent: print 'Pinging {}, attempts remaining {}'.format(dest, n-1)
			self.send(self._proto_ping_to(dest))
			if double: self.send(self._proto_ping_to(dest))
			send_time = time.time()
			while self._ping_tracker[dest] == '' and time.time()-send_time < 3:
				time.sleep(0.01) 
			if not silent:
				if self._ping_tracker[dest]!= '':
					print 'Ping to {} successful at {}, completed in {} seconds'.format(dest, 1/self.half_pulse, time.time()-send_time)
					return True
				else:
					print 'Ping to {} failed'.format(dest)
			n-=1
			if n>0: time.sleep(1)
			
		return self._ping_tracker[dest]!= ''


	def _handle_ping(self, ping):
		s,d,m = ping
		if m==self.PING:
			self.send(self._proto_pong_to(d))
		elif m==self.PONG:
			self._ping_tracker[s] = m


	def _binary_reader(self, m):
		try:
			ch = self.to_char(m)
			if self.debug: print ch
			if ch==self.MSG_CONTAINER[0]:
				self._temp_msg=ch
			elif ch==self.MSG_CONTAINER[1]:
				if self._temp_msg:
					msg = self._temp_msg[1:]
					ping = self._proto_ping_sniffer(msg)
					if ping: 
						self._handle_ping(ping)
					else:
						for func in self._msg_subscriptions:
							func(msg)
					self._temp_msg = ''
					if self.debug: print "Message =",msg
			else:
				self._temp_msg += ch
				
			if self.debug==2: print 'Compiling command ...', self._temp_msg, ';', str(m)
		except Exception as e:
			if self.debug: print str(e), str(m)


	def subscribe(self, func):
		self._msg_subscriptions.append(func)
		return True





if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', help='Debug modes 0, 1 or 2', action="count", default=0)
	

	args = parser.parse_args()
	debug = args.debug
	if debug > 3: debug=3
	print 'debug =', debug

	def demo_printer(msg):
		print 'Received -> '+str(msg)
		if '3way' in msg:
			print 'replying'
			RF.send('Upgrade to 4way')

	start = time.time()
	RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=debug)
	if args.samp: RF.half_pulse = RF.short_delay*args.samp
	RF.subscribe(demo_printer)
	RF.listen()
	if RF.ping(RF.__id__, n=3, silent=False):
		RF.send('3way h-shake is an extremely long message. Seems like it will shit out.')
	print '3way completed in {}'.format(time.time()-start)
	time.sleep(4)
	RF.terminate()
		

	# RFd = RFDriver(tx_pin=tx, rx_pin=rx, debug=1)
	# RFd.listen()
	# RFd.transmit_binary('10101010')
	# time.sleep(3)
	# RFd.terminate()




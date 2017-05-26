#!/usr/bin/python
__author__ = "Shashank Gopikrishna"
__version__ = "0.0.1"
__email__ = "shashank.gopikrishna@gmail.com"


import RPi.GPIO as gpio
import time
import threading

tx = 37
rx = 40


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def saltGen(size=64):
	"""Generates salt for password encryption"""
	import string, random
	alph = str(string.lowercase+string.digits)*2
	return str(''.join(random.sample(alph, size)))





class RFProtocol(object):
	short_delay = 0.001
	long_delay = short_delay*2
	half_pulse = short_delay*0.3
	padByte = '10011111'
	lastBit = '0'

	

class RFDriver(RFProtocol):
	'''
	Exposes low level RF transmission and reception methods.
	debug = 1 displays received character

	RF = RFDriver(tx_pin=tx, rx_pin=rx, debug=1)
	RF.listen()
	RF.transmit_binary('10101010')
	time.sleep(1)
	print RF._fetch_from_buffer()
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
		gpio.setmode(gpio.BOARD)
		gpio.setwarnings(False)
		gpio.setup(self.TX, gpio.OUT, initial=gpio.LOW)
		gpio.setup(self.RX, gpio.IN, pull_up_down=gpio.PUD_DOWN)


	def _defaultSubscription(self, bn):
		print 'Message Received->', str(bn), '=', self.to_char(bn)


	def transmit_binary(self, code):
		bn_encl = self.padByte+code+self.lastBit
		gpio.setmode(gpio.BOARD)
		for i in bn_encl:
			if i == '1':
				gpio.output(self.TX, 1)
				time.sleep(self.short_delay)
				gpio.output(self.TX, 0)
				time.sleep(self.long_delay)
			elif i == '0':
				gpio.output(self.TX, 1)
				time.sleep(self.long_delay)
				gpio.output(self.TX, 0)
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
			gpio.setmode(gpio.BOARD)
			gpio.setup(self.RX, gpio.IN, pull_up_down=gpio.PUD_DOWN)
			if gpio.input(self.RX):
				high_count+=1
			else:
				if high_count: 
					if self.debug==3: print 'high:',high_count
					self._buffer += '0' if high_count < 4 else '1'
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
				try:
					s = string.index(self.padByte)+len(self.padByte)
					if s:
						if self.debug: print 'message from {} to {} in {}'.format(s, s+8, string)
						for func in self._subscriptions:
							try:
								func(string[s:s+8])
								# print 'LastChar = ', string[s+8]
							except Exception as e: 
								if self.debug==2: print str(e)
						string = string[s+8:]
				except ValueError:
					pass
				except Exception as e:
					if self.debug: print str(e)
			time.sleep(0.1)
		print '**Ended RF processing thread'


	def listen(self):
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
		




class RFMessageProtocol2(object):
	__config__ = 'MASTER'
	__id__ = 'M'
	PING='Pi'
	PONG='Po'
	MSG_CONTAINER = ('<','>')

	PROTOMAP = DotDict({
			PING:PONG
		})

	def _proto_contain(self, msg):
		return MSG_CONTAINER[0]+str(msg)+MSG_CONTAINER[1]

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



				  


class RFMessenger2(RFDriver, RFMessageProtocol2):
	'''
	Higher level access to transmission and message handling.

	RF = RFProtocol(tx_pin=tx, rx_pin=rx, debug=1)
	RF.listen()
	print 'PING =', RF.PING, 'PONG =', RF.PONG

	# Pinging self
	if RF.ping(RF.address, n=5):  
		RF.broadcast('Ping success!')
		print 'Ping success!->',i,'\n'
	time.sleep(3)

	#Long message
	RF.broadcast('Hello and welcome to the RF World!')
	time.sleep(4)

	RF.send_to('Hello and welcome to the RF World!', RF.address)
	time.sleep(4)
	RF.terminate()

	# Message packet format = SRC|DEST|SERVICE:COMMAND
	'''

	def __init__(self, tx_pin, rx_pin, debug=0):
		super(RFMessenger2, self).__init__(tx_pin, rx_pin, debug)
		self._command_tracker = {}
		self._tracker_timeout = 5
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
		if self.debug==2: print 'Sent->', ch, 'as', bn
		return True


	def send(self, string, n=1, delay=1):
		msg = self._proto_contain(string)
		for i in xrange(n):
			for ch in msg:
				self.transmit_char(ch)
			if n>1: time.sleep(delay)
		return True



	def ping(self, dest, n=1):
		self._ping_tracker[dest] = ''
		while self._ping_tracker[dest] != self.PONG and n>0:
			print 'Pinging {}'.format(dest)
			self.send(self._proto_ping_to(dest))
			send_time = time.time()
			while self._ping_tracker[dest]!= '' and time.time()-send_time < 4:
				time.sleep(0.5)
			if self.debug: 
				if self._ping_tracker[dest]!= '':
					print 'Ping to {} successful in {} seconds'.format(dest, time.time()-send_time)
				else:
					print 'Ping to {} failed'.format(dest)
			n-=1
		return self._ping_tracker[dest]!= ''


	def _handle_ping(self, ping):
		s,d,m = ping
		if m==self.PING:
			self.send(self._proto_pong_to(dest))
		elif m==self.PONG:
			self._ping_tracker[s] = m


	def _binary_reader(self, m):
		try:
			ch = self.to_char(m)
			if ch==self.MSG_CONTAINER[0]:
				self._temp_msg=ch
			elif ch==self.MSG_CONTAINER[1]:
				msg = self._temp_msg[1:]
				ping = self._proto_ping_sniffer(msg)
				if ping: 
					self._handle_ping(ping)
				else:
					for func in self._msg_subscriptions:
						func(msg)
				self._temp_msg = ''
				if debug: print "Message =",msg
			else:
				self._temp_msg += ch
				
			if debug==2: print 'Compiling command ...', self._temp_msg, ';', str(m)
		except Exception as e:
			if self.debug: print str(e), str(m)


	def subscribe(self, func):
		self._msg_subscriptions.append(func)
		return True


class RFMessageProtocol(object):
	__config__ = 'MASTER'
	PING='Pi'
	PONG='Po'
	PROTOMAP = DotDict({
			PING:PONG
		})

class RFMessenger(RFDriver, RFMessageProtocol):
	'''
	Higher level access to transmission and message handling.

	RF = RFProtocol(tx_pin=tx, rx_pin=rx, debug=1)
	RF.listen()
	print 'PING =', RF.PING, 'PONG =', RF.PONG

	# Pinging self
	if RF.ping(RF.address, n=5):  
		RF.broadcast('Ping success!')
		print 'Ping success!->',i,'\n'
	time.sleep(3)

	#Long message
	RF.broadcast('Hello and welcome to the RF World!')
	time.sleep(4)

	RF.send_to('Hello and welcome to the RF World!', RF.address)
	time.sleep(4)
	RF.terminate()

	# Message packet format = SRC|DEST|SERVICE:COMMAND
	'''

	def __init__(self, tx_pin, rx_pin, address=None, debug=0):
		super(RFMessenger, self).__init__(tx_pin, rx_pin, debug)
		if not address: self.address = 'M'
		self._temp_command = ''
		self._ping_tracker = {}
		self.subscribe_binary(self._binary_reader)

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


	def _bind_protocol(self, command, dest='AL'):
		'''src|dest|command'''
		return '{}|{}|{}'.format(self.address, dest, command)


	def send_string(self, string, n=1, delay=1):
		mess_encl = '<'+str(string)+'>'
		for i in xrange(n):
			for ch in mess_encl:
				bn = self.to_binary(ch)
				if debug==2: print 'Sent->', ch, 'as', bn
				self.transmit_binary(bn)
			if n>1: time.sleep(delay)
		return True


	def broadcast(self, msg):
		m = self._bind_protocol(str(msg))
		if debug: print 'Broadcasting ->', m
		self.send_string(m)
		return True


	def send_to(self, msg, dest):
		m = self._bind_protocol(str(msg), dest)
		if debug: print 'Sending to {} -> {}'.format(dest, m)
		self.send_string(m)
		return True


	def ping(self, dest, n=10):
		self._ping_tracker[dest] = ''
		while self._ping_tracker[dest] != self.PONG and n>0:
			print 'Pinging {}'.format(dest)
			self.send_to(self.PING, dest)
			time.sleep(3.5)
			n-=1
		# if self.debug: print self._ping_tracker
		return self._ping_tracker[dest]!= ''


	def _binary_reader(self, m):
		try:
			ch = self.to_char(m)
			if ch=='<':
				self._temp_command=ch
			elif ch=='>':
				command = self._temp_command[1:]
				self._process_command(command)
				self._temp_command = ''
				if debug: print "Message =",command
			else:
				self._temp_command += ch
				
			if debug==2: print 'Compiling command ...', self._temp_command, ';', str(m)
		except Exception as e:
			if self.debug: print str(e), str(m)


	def _process_command(self, command):
		try:
			s,d,c = command.split('|')[-3:]
			print '{} sent {} to {} at {}'.format(s,c,d,time.time()), ';', command
			time.sleep(0.8)
			print self.PROTOMAP
			if c in self.PROTOMAP:
				if d==self.address or d=='AL':
					self.send_to(self.PROTOMAP[c], s)
					return True
			if c==self.PONG: 
				self._ping_tracker[s]=c
				return True
		except Exception as e:
			if self.debug: print str(e), str(command)
		print "Default message display =",command




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', help='Debug modes 0, 1 or 2', action="count", default=0)
	args = parser.parse_args()
	debug = args.debug
	if debug > 3: debug=3
	print 'debug =', debug
	RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=debug)
	RF.listen()

	#Pinging self
	print 'PING =', RF.PING, 'PONG =', RF.PONG
	for i in xrange(3):
		if RF.ping(RF.address, n=5):
			RF.broadcast('Ping success!')
			print 'Ping success!->',i,'\n'
		time.sleep(3)

	#Long message
	RF.broadcast('Hello and welcome to the RF World!')
	time.sleep(4)

	RF.send_to('Hello and welcome to the RF World!', RF.address)
	time.sleep(4)

	RF.terminate()



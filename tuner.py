from txrx import RFMessenger, gpio, cpuinfo
import threading, time


class RFTuner(RFMessenger):

	def __init__(self, tx_pin, rx_pin, debug=0):
		super(RFTuner, self).__init__(tx_pin, rx_pin, debug)
		gpio.add_event_detect(rx_pin, gpio.BOTH, callback=self.listen_falling, bouncetime=100)
		# gpio.add_event_detect(rx_pin, gpio.RISING, callback=self.listen_rising)
		self.high_tracker = 0
		self.processThread = threading.Thread(target=self._processor)
		self.processThread.start()
		time.sleep(0.5)

	
	def listen_rising(self):
		print 'rose'

	def listen_falling(self, x):
		if gpio.input(x):
			self.high_tracker+=1
		else:
			if self.high_tracker > 1 and self.high_tracker < 8:
				if self.high_tracker < 4:
					bit = '0' if cpuinfo.this_is_a_pi() else '1'
				else: 
					bit = '1' if cpuinfo.this_is_a_pi() else '0'
				self._buffer += bit
				if self.debug==3: print 'high:',self.high_tracker, '\t', bit


if __name__ == '__main__':
	debug = 2
	if cpuinfo.this_is_a_chip():
		RF = RFTuner(tx_pin='CSID0', rx_pin='XIO-P0', debug=debug)
	else:
		RF = RFTuner(tx_pin=37, rx_pin=40, debug=debug)
	p = raw_input()
	if p[0]=='p':
		RF.ping(silent=False)
		time.sleep(2)
		print RF._fetch_from_buffer()
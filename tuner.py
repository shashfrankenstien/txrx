from txrx import RFMessenger, gpio
import threading, time


class RFTuner(RFMessenger):

	def __init__(self, tx_pin, rx_pin, debug=0):
		super(RFTuner, self).__init__(tx_pin, rx_pin, debug)
		gpio.add_event_detect(rx_pin, gpio.BOTH, callback=self.listen_falling)
		gpio.add_event_detect(rx_pin, gpio.RISING, callback=self.listen_rising)

	
	def listen_rising(self):
		print 'rose'

	def listen_falling(self, x):
		print x
		print 'fell'


if __name__ == '__main__':
	RF = RFTuner(tx_pin='CSID0', rx_pin='XIO-P0')
	p = raw_input()
	if p[0]=='p':
		RF.ping(silent=False)
		time.sleep(2)
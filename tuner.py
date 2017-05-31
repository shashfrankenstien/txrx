from txrx import RFMessenger
import threading

class RFTuner(RFMessenger):

	def __init__(self, tx_pin, rx_pin, debug=0):
		super(RFTuner, self).__init__(tx_pin, rx_pin, debug)
	
	def listen_callback(self):
		pass
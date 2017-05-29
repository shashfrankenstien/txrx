from txrx import RFMessenger, rand_id_gen
import time


tx = 37
rx = 40


class AddressMap(RFMessenger):
	def __init__(self, tx_pin=tx, rx_pin=rx, ID=None):
		super(RFMessenger2, self).__init__(tx_pin, rx_pin)
		if ID: 
			self.setID(ID)
		else:
			self.setID(rand_id_gen(2))
		self._discovered = False

	def setID(self, ID):
		self.__id__ = ID

	# def discover_me(self):
	# 	while


start = time.time()
RF = RFMessenger(tx_pin=tx, rx_pin=rx)

def demo_printer(msg):
	print 'Received -> '+str(msg)
	if '3way' in msg:
		print 'replying'
		RF.send('Upgrade to 4way')

RF.subscribe(demo_printer)
RF.listen()
if RF.ping(RF.__id__, n=3, silent=False):
	RF.send('3way h-shake is an extremely long message. Seems like it will shit out.')
print '3way completed in {}'.format(time.time()-start)
time.sleep(4)
RF.terminate()
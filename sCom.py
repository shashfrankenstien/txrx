from txrx import RFMessenger

start = time.time()
RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=debug)

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
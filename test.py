from txrx import RFMessenger, cpuinfo
import time
import argparse
import threading


def fwayHshake(args, debug):

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

def bitwise(args, debug=0):
	RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=debug)
	if args.samp: RF.half_pulse = RF.short_delay*args.samp
	RF.listen()
	RF.transmit_binary(args.bitwise)
	time.sleep(3)
	RF.terminate()


def tune(args, debug=0, start=0.18, end=0.330, step=0.001):
	points = []
	t = start

	RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=debug)
	if args.samp: RF.half_pulse = RF.short_delay*args.samp
	RF.listen()

	while t<=end:
		RF.half_pulse = RF.short_delay*t
		print '#############    sleep time = {}'.format(t)
		start = time.time()
		if RF.ping(RF.__id__, silent=False):
			points.append((t, time.time()-start))
		t += step
	RF.terminate()

	import json
	for i in points: print i



def cli(args, debug=0):
	def defFunc(m):
		print m

	RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=debug)
	if args.samp: RF.half_pulse = RF.short_delay*args.samp
	RF.subscribe(defFunc)
	RF.listen()
	
	def ping(addr=None):
		if addr:
			RF.ping(addr, silent=False)
		else:
			RF.ping(RF.__id__, silent=False)

	def command():
		while True:
			c = raw_input()
			if c:
				if c[0]=='p':
					ping(c[1:])
				elif c[0]=='q':
					break
			print 'unrecognized'

	command()
	RF.terminate()



if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--tx', help='Transmitter pin')
	parser.add_argument('-r','--rx', help='Receiver pin')

	parser.add_argument('-d', '--debug', help='Debug modes 0, 1 or 2', action="count", default=0)
	parser.add_argument('-u', '--tune', help='Tuning monitor', action="store_true")
	parser.add_argument('-c', '--cli', help='CLI to test ping', action="store_true")
	parser.add_argument('-b', '--bitwise', help='Bitwise send', type=str)
	parser.add_argument('-s', '--samp', help='Receiver thread sampling factor', type=float)

	args = parser.parse_args()

	if cpuinfo.this_is_a_pi():
		tx = int(args.tx) if args.tx else 37
		rx = int(args.rx) if args.tx else 40
	else:
		tx = args.tx if args.tx else 'CSID0'
		rx = args.rx if args.rx else 'CSID1'

	

	args = parser.parse_args()
	debug = args.debug
	if debug > 3: debug=3
	print 'debug =', debug

	if args.tune:
		start, end, step = [float(i.strip()) for i in raw_input('start, end, step: ').split(',')]
		tune(args, debug, start, end, step)
	elif args.cli:
		cli(args, debug)

	elif args.bitwise:
		bitwise(args, debug)
	else:
		fwayHshake(args, debug)
		
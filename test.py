from txrx import RFMessenger
import time
import argparse
import threading

parser = argparse.ArgumentParser()
parser.add_argument('-t','--tx', help='Transmitter pin', type=int)
parser.add_argument('-r','--rx', help='Receiver pin', type=int)

args = parser.parse_args()
tx = args.tx
rx = args.rx

def defFunc(m):
	print m

def ping():
	RF.ping(RF.__id__, silent=False)

def command():
	while True:
		c = raw_input()
		if c:
			if c=='p':
				ping()
			elif c=='q':
				break
		print 'unrecognized'

RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=2)
RF.subscribe(defFunc)
RF.listen()

command()

RF.terminate()
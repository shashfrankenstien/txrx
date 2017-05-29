from txrx import RFMessenger
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t','--tx' help='Transmitter pin')
parser.add_argument('-r','--rx' help='Receiver pin')

args = parser.parse_args()
tx = args.tx
rx = args.rx

def defFunc(m):
	print m


RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=2)
RF.subscribe(defFunc)
RF.listen()
time.sleep(1)
RF.ping(RF.__id__, silent=False)


time.sleep(20)
RF.terminate()
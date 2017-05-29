from txrx import RFMessenger
import time

def defFunc(m):
	print m

tx = 37
rx = 40

RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=2)
RF.subscribe(defFunc)
RF.listen()
time.sleep(1)
RF.ping(RF.__id__, silent=False)


time.sleep(20)
RF.terminate()
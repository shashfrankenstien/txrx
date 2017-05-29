from txrx import RFMessenger


def defFunc(m):
	print m

tx = 35
rx = 31

RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=2)
RF.subscribe(defFunc)
RF.listen()
RF.ping(RF.__id__, silent=False)

import time
time.sleep(20)
RF.terminate()
# txrx
Python package for interfacing _433MHz RF tx-rx modules_ with a Raspberry pi
Offers low and high level access to transmission and message handling.

####Usage
```python
from txrx import RFMessenger
import time

def demo_printer(msg):
	print 'Received ->', str(msg)
	
RF = RFMessenger(tx_pin=tx, rx_pin=rx, debug=debug)
RF.subscribe(demo_printer)
RF.listen()
RF.ping(dest=RF.__id__, n=3, silent=False)

RF.send('string')
time.sleep(3)
RF.terminate()
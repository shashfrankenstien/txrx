# txrx
Python package for interfacing _433MHz RF tx-rx modules_ with a Raspberry pi.
Offers low and high level access to transmission and message handling.

####Usage
```python
from txrx import RFMessenger
import time

def demo_printer(msg):
	print 'Received ->', str(msg)
	
RF = RFMessenger(tx_pin=tx, rx_pin=rx)
RF.subscribe(demo_printer)
RF.listen()

if RF.ping(dest=RF.__id__, n=3, silent=False):
	RF.send('3way h-shake')
time.sleep(3)
RF.terminate()
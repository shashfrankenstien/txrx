# txrx
Python package for interfacing _433MHz RF tx-rx modules_ with a Raspberry pi
Offers low and high level access to transmission and message handling.

####Usage
```python

RF = RFProtocol(tx_pin=tx, rx_pin=rx, debug=1)
RF.listen()
print 'PING =', RF.PING, 'PONG =', RF.PONG

# Pinging self
if RF.ping(RF.address, n=5):  
	RF.broadcast('Ping success!')
	print 'Ping success!->',i,'\n'
time.sleep(3)

#Long message
RF.broadcast('Hello and welcome to the RF World!')
time.sleep(4)

RF.send_to('Hello and welcome to the RF World!', RF.address)
time.sleep(4)
RF.terminate()

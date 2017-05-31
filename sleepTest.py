from datetime import datetime
import time

def check_sleep(amount):
    start = datetime.now()
    time.sleep(amount)
    end = datetime.now()
    delta = end - start
    return delta.seconds + delta.microseconds/1000000.0

def sleeperror(amount=0.050, n=100):
	error = 0
	for i in range(n):
	    error += abs(check_sleep(amount) - amount)
	error /= n
	return error

if __name__ == '__main__':
	print sleeperror(0.001)

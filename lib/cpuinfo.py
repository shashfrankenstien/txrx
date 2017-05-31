class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


CPUInfo = dotdict()

try:
	with open('/proc/cpuinfo', 'r') as cpuinfo:
		for i in cpuinfo:
			try:
				k, v = i.strip().split(':')
				CPUInfo[str(k).strip()] = str(v).strip()
			except: pass
except: pass

def this_is_a_pi():
	if 'Hardware' in CPUInfo and 'BCM' in CPUInfo.Hardware:
		return True
	return False

def this_is_a_chip():
	if 'Hardware' in CPUInfo and 'Allwinner' in CPUInfo.Hardware:
		return True
	return False

def who_am_i():
	if this_is_a_chip():
		return 'NTC CHIP'
	if this_is_a_pi():
		return 'RASPBERRY PI'
	else:
		return 'Device is not compatible'


if __name__ == '__main__':
	print who_am_i()
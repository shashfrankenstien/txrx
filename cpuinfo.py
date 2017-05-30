class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


CPUInfo = dotdict()

with open('/proc/cpuinfo', 'r') as cpuinfo:
	for i in cpuinfo:
		try:
			k, v = i.strip().split(':')
			CPUInfo[str(k).strip()] = str(v).strip()
		except:
			pass

def this_is_a_pi():
	if 'BCM' in CPUInfo.Hardware:
		return True
	else: return False

def this_is_a_chip():
	if 'Allwinner' in CPUInfo.Hardware:
		return True
	else: return False

def who_am_i():
	if this_is_a_chip():
		return 'NTC CHIP'
	if this_is_a_pi():
		return 'RASPBERRY PI'


if __name__ == '__main__':
	print who_am_i()
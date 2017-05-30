class CPUInfo(dict):
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

	def __init__(self):
		with open('/proc/cpuinfo', 'r') as cpuinfo:
			for i in cpuinfo:
				try:
					k, v = i.strip().split(':')
					self[k] = v
				except:
					pass


if __name__ == '__main__':
	c = cpuinfo()
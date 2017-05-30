class CPUInfo(dict):
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

	with open('/proc/cpuinfo', 'r') as cpuinfo:
		for i in cpuinfo:
			try:
				k, v = i.strip().split(':')
				self[str(k).strip()] = str(v).strip()
			except:
				pass

	def this_is_a_pi(self):
		if 'BCM' in self.Hardware:
			return True
		else: return False

	def this_is_a_chip(self):
		if 'Allwinner' in self.Hardware:
			return True
		else: return False

	def who_am_i(self):
		if self.this_is_a_chip():
			return 'NTC CHIP'
		if self.this_is_a_pi():
			return 'RASPBERRY PI'


if __name__ == '__main__':
	print CPUInfo.who_am_i()
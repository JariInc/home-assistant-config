from ruuvitag_sensor.ruuvi import RuuviTagSensor

class Ruuvitag(object):
	macs = []
	datas = []
	timeout = 0

	def __init__(self, macs, interval):
		self.macs = macs
		self.timeout = interval

	def update(self):
		self.datas = RuuviTagSensor.get_data_for_sensors(self.macs, self.timeout)

	def getMeasurement(self, mac):
		if mac in self.datas:
			data = self.datas[mac]
			del self.datas[mac]
			return data
		else:
			return None

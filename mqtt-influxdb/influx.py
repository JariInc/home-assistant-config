import logging
from influxdb import InfluxDBClient

class Influx(object):
	logger = None
	client = None

	def __init__(self, username, password, host, port=8086):
		self.logger = logging.getLogger('mqtt-influxdb.influxdb')
		self.client = InfluxDBClient(host=host, port=port, username=username, password=password)

	def write(self, database, measurement, tags, fields, time):
		data = {
			"measurement": measurement,
			"tags": tags,
			"time": time.isoformat(),
			"fields": fields,
		}

		self.client.switch_database(database)
		self.client.write_points([data])
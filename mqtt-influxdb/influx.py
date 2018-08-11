import logging
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

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

		self.logger.debug("Saving data %s", data)

		self.client.switch_database(database)

		try:
			self.client.write_points([data])
		except InfluxDBClientError as e:
			self.logger.error('InfluxDB error: %s', str(e))
import logging
import time
import datetime
import os
import json
from mqtt import MQTTClient
from influx import Influx
from dotenv import load_dotenv
from util import Util

load_dotenv()

class MQTTInfluxDBBridge(object):
	logger = None
	mqtt = None
	influx = None
	utll = None
	
	def __init__(self):
		self.logger = logging.getLogger('mqtt-influxdb')
		self.logger.setLevel(logging.DEBUG)
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		ch.setFormatter(formatter)
		self.logger.addHandler(ch)
		self.logger.propagate = False
		self.logger.info('Starting mqtt-influxdb')

		# Util
		self.util = Util()

		# InfluxDB
		self.influx = Influx(
			os.getenv('INFLUXDB_USER'),
			os.getenv('INFLUXDB_PASSWORD'),
			os.getenv('INFLUXDB_HOST')
		)

		# MQTT
		self.mqtt = MQTTClient(os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_BROKER_HOST'))
		self.mqtt.connect()

		# Ruuvitags
		ruuvitag_macs = os.getenv('RUUVITAG_MACS').split(',')
		for mac in ruuvitag_macs:
			self.mqtt.subscribe('ruuvitag/' + mac, 0, self.ruuvitag_callback)

		# HVAC
		self.mqtt.subscribe('hvac/toshiba-63200289/pid/state', 0, self.hvac_callback)

		# BME280
		bme280_ids =  os.getenv('BME280_IDS').split(',')
		for bme280_id in bme280_ids:
			self.mqtt.subscribe('bme280/' + bme280_id, 0, self.bme280_callback)

		self.logger.info('MQTT connected')

	def hvac_callback(self, client, userdata, message):
		payload = json.loads(message.payload.decode('utf-8'), parse_int=float)
		now = datetime.datetime.now()
		self.influx.write(
			'hvac', 
			'state', 
			{'device': 'toshiba-63200289'},
			payload,
			now
		)

	def ruuvitag_callback(self, client, userdata, message):
		payload = json.loads(message.payload.decode('utf-8'), parse_int=float)
		topic_parts = message.topic.split('/')
		mac = topic_parts[1]
		now = datetime.datetime.now()

		payload['dew_point'] = self.util.dewPoint(payload['temperature'], payload['humidity'])
		payload['absolute_humidity'] = self.util.absoluteHumidity(payload['temperature'], payload['humidity'])

		self.influx.write(
			'ruuvitag', 
			'environment', 
			{'sensor': mac},
			payload,
			now
		)

	def bme280_callback(self, client, userdata, message):
		payload = json.loads(message.payload.decode('utf-8'), parse_int=float)
		topic_parts = message.topic.split('/')
		bme280_id = topic_parts[1]
		now = datetime.datetime.now()

		payload['dew_point'] = self.util.dewPoint(payload['temperature'], payload['humidity'])
		payload['absolute_humidity'] = self.util.absoluteHumidity(payload['temperature'], payload['humidity'])

		self.influx.write(
			'bme280', 
			'environment', 
			{'sensor': bme280_id},
			payload,
			now
		)

if __name__ == '__main__':
	ctrl = MQTTInfluxDBBridge()

	while True:
		time.sleep(1)
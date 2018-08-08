import logging
import time
import datetime
import os
import json
from mqtt import MQTTClient
from influx import Influx
from dotenv import load_dotenv

load_dotenv()

class MQTTInfluxDBBridge(object):
	logger = None
	mqtt = None
	influx = None
	
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

		# subscribe
		#self.mqtt.subscribe(self.topic_prefix + '/fan/set', 0, self.set_fan)

		self.logger.info('MQTT connected')

	def hvac_callback(self, client, userdata, message):
		payload = json.loads(message.payload.decode('utf-8'))
		now = datetime.datetime.now()
		self.influx.write(
			'hvac', 
			'state', 
			{'device': 'toshiba-63200289'},
			payload,
			now
		)

	def ruuvitag_callback(self, client, userdata, message):
		payload = json.loads(message.payload.decode('utf-8'))
		topic_parts = message.topic.split('/')
		mac = topic_parts[1]
		now = datetime.datetime.now()

		self.influx.write(
			'ruuvitag', 
			'environment', 
			{'sensor': mac},
			payload,
			now
		)

if __name__ == '__main__':
	ctrl = MQTTInfluxDBBridge()

	while True:
		time.sleep(1)
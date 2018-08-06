import logging
import time
import os
import json
from mqtt import MQTTClient
from pid import PID
from dotenv import load_dotenv

load_dotenv()

class HVACPIDController(object):
	logger = None
	mqtt = None
	pid = None

	temp_request = 22
	temp_measure = 22
	temp_set = 22
	fan_set = 3
	mode = 'COOL'

	def __init__(self):
		self.logger = logging.getLogger('hvac-pid')
		self.logger.setLevel(logging.DEBUG)
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		ch.setFormatter(formatter)
		self.logger.addHandler(ch)
		self.logger.propagate = False
		self.logger.info('Starting hvac-pid')

		# MQTT
		self.mqtt = MQTTClient(os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_BROKER_HOST'))
		self.mqtt.connect()
		self.mqtt.subscribe(os.getenv('MQTT_PID_TOPIC'), 1, self.set_update_callback)
		self.mqtt.subscribe(os.getenv('MQTT_TEMP_TOPIC'), 0, self.temp_update_callback)
		self.logger.info('MQTT connected')

		self.pid = PID(
			float(os.getenv('PID_KP')), 
			float(os.getenv('PID_KI')), 
			float(os.getenv('PID_KD'))
		)

	def iterate(self):
		# temp_set
		pid_set_temp = self.pid.iterate(self.temp_request, self.temp_measure)
		self.temp_set = int(round(min(30, max(17, pid_set_temp))))
		self.logger.info('Set temperature %s', self.temp_set)
		
		# fan_set
		error = self.pid.previous_error
		error_abs = abs(error)
		is_heat = self.mode == 'HEAT'

		# if overshoot over 0.5 degrees, set fan to 2
		if (is_heat and error < 0.5) or (not is_heat and error > 0.5):
			self.fan_set = 2
		elif error_abs < 1.0:
			self.fan_set = 3
		elif error_abs < 2.0:
			self.fan_set = 4
		else:
			self.fan_set = 5
		self.logger.info('Set fan %s', self.fan_set)

		self.setHVAC()

	def set_update_callback(self, client, userdata, message):
		payload_json = json.loads(message.payload.decode("utf-8"))
		self.logger.debug('Received new request values %s', payload_json)

		if 'mode' in payload_json and payload_json.mode in ['HEAT', 'COOL']:
			self.mode = payload_json['mode']
			self.logger.info('Mode %s', self.mode)

		if 'temperature' in payload_json:
			self.temp_request = float(payload_json['temperature'])
			self.logger.info('Temperature request %g', self.temp_request)

	def temp_update_callback(self, client, userdata, message):
		payload_json = json.loads(message.payload.decode("utf-8"))
		self.logger.info('Received temperature measurement %s', payload_json['temperature'])
		self.temp_measure = payload_json['temperature']
		self.logger.info('PID iteration')
		self.iterate()

	def setHVAC(self):
		topic = os.getenv('MQTT_HVAC_TOPIC')
		message = json.dumps({
			'power': True,
			'mode': self.mode,
			'temperature': self.temp_set,
			'fan': self.fan_set,
		})
		self.mqtt.publish(topic, message, 1)

if __name__ == '__main__':

	ctrl = HVACPIDController()

	while True:
		time.sleep(1)
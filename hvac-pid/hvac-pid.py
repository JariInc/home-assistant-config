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

	temp_request = 21
	temp_measure = 21
	temp_set = 21
	fan_set = 3
	mode = 'auto'
	power = True
	manual = False

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

		# PID
		self.pid = PID(
			float(os.getenv('PID_KP')), 
			float(os.getenv('PID_KI')), 
			float(os.getenv('PID_KD'))
		)

		# MQTT
		self.topic_prefix = os.getenv('MQTT_PID_TOPIC_PREFIX')
		self.mqtt = MQTTClient(os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_BROKER_HOST'))
		self.mqtt.connect()

		# subscribe
		self.mqtt.subscribe(os.getenv('MQTT_TEMP_TOPIC'), 0, self.temp_update_callback)
		self.mqtt.subscribe(self.topic_prefix + '/mode/set', 0, self.set_mode)
		self.mqtt.subscribe(self.topic_prefix + '/temperature/set', 0, self.set_temp)
		self.mqtt.subscribe(self.topic_prefix + '/power/set', 0, self.set_power)
		self.mqtt.subscribe(self.topic_prefix + '/fan/set', 0, self.set_fan)

		self.logger.info('MQTT connected')

		self.publish_temp()
		self.publish_mode()
		self.publish_power()

	def iterate(self):
		if self.manual:
			self.logger.info('Manual mode, skipping PID iteration')
			self.temp_set = self.temp_request
		else:
			# temp_set
			pid_set_temp = self.pid.iterate(self.temp_request, self.temp_measure)
			self.temp_set = int(round(min(30, max(17, pid_set_temp))))
			self.logger.info('Set temperature %s', self.temp_set)
			
			# fan_set
			error = self.pid.previous_error
			error_abs = abs(error)
			is_heat = self.mode == 'heat'

			# if overshoot over 2/1 degrees, set fan to 1
			if (is_heat and error < 2.0) or (not is_heat and error > 1):
				self.fan_set = 1
			# if overshoot over 0.5 degrees, set fan to 2
			elif (is_heat and error < 1.0) or (not is_heat and error > 0.5):
				self.fan_set = 2
			elif error_abs < 1.0:
				self.fan_set = 3
			elif error_abs < 2.0:
				self.fan_set = 4
			else:
				self.fan_set = 5
			self.logger.info('Set fan %s', self.fan_set)

			if not is_heat and error > 1.0:
				self.power = False
			else:
				self.power = True

			self.publish_state()
		
		self.setHVAC()

	def temp_update_callback(self, client, userdata, message):
		payload_json = json.loads(message.payload.decode('utf-8'))
		self.logger.info('Received temperature measurement %s', payload_json['temperature'])
		self.temp_measure = payload_json['temperature']
		self.logger.info('PID iteration')
		self.iterate()
		self.publish_temp()

	def setHVAC(self):
		topic = os.getenv('MQTT_HVAC_TOPIC')
		message = json.dumps({
			'power': self.power,
			'mode': self.mode.upper(),
			'temperature': self.temp_set,
			'fan': self.fan_set,
		})

		self.logger.debug('Controlling HVAC with command %s', message)
		self.mqtt.publish(topic, message, 1)

	def set_mode(self, client, userdata, message):
		mode = message.payload.decode('utf-8')
		previous_is_manual = self.manual

		if mode == 'manual':
			self.manual = True
			self.mode = 'auto'
			self.logger.info('Set mode to manual')
			self.publish_mode()
			self.iterate()
		elif mode in ['heat', 'cool']:
			self.manual = False
			self.mode = mode

			self.logger.info('Set mode to %s', self.mode)

			# reset PID if switching between manual and pid modes
			if previous_is_manual != self.manual:
				self.pid.reset()

			self.publish_mode()
			self.iterate()

	def publish_mode(self):
		topic = self.topic_prefix + '/mode/state'
		
		if self.manual:
			mode = 'manual'
		else:
			mode = self.mode

		self.mqtt.publish(topic, mode, 1, True)

	def set_temp(self, client, userdata, message):
		temp = float(message.payload.decode('utf-8'))

		if temp >= 17 and temp <= 30:
			self.temp_request = temp
			self.logger.info('Set temperature request to %s', self.temp_request)
			self.publish_temp()
			self.iterate()


	def publish_temp(self):
		self.mqtt.publish(self.topic_prefix + '/temperature/state', self.temp_request, 1, True)
		self.mqtt.publish(self.topic_prefix + '/measured_temperature', self.temp_measure, 1, True)

	def set_power(self, client, userdata, message):
		self.power = str(message.payload.decode('utf-8')) == 'true'
		self.logger.info('Set power to %s', self.power)
		self.publish_power()
		self.iterate()

	def publish_power(self):
		topic = self.topic_prefix + '/power/state'
		if self.power:
			message = 'true'
		else:
			message = 'false'

		self.mqtt.publish(topic, message, 1, True)

	def set_fan(self, client, userdata, message):
		fan = int(message.payload.decode('utf-8'))

		if fan >= 1 and fan <= 5:
			self.fan_set = fan
			self.logger.info('Set fan to %s', self.fan_set)
			self.publish_fan()
			self.iterate()

	def publish_fan(self):
		topic = self.topic_prefix + '/fan/state'
		
		if self.manual:
			fan = self.fan_set
		else:
			fan = 'auto'

		self.mqtt.publish(topic, fan, 1, True)

	def publish_state(self):
		topic = os.getenv('MQTT_PID_TOPIC_PREFIX') + '/state'
		message = json.dumps({
			'mode': self.mode,
			'manual': self.manual,
			'temperature_request': self.temp_request,
			'temperature_set': self.temp_set,
			'temperature_measure': self.temp_measure,
			'temperature_error': self.pid.previous_error,
			'fan': self.fan_set,
			'power': self.power,
			'Kp': self.pid.Kp,
			'Ki': self.pid.Ki,
			'Kd': self.pid.Kd,
			'integral': self.pid.integral,
		})
		self.mqtt.publish(topic, message, 1)

if __name__ == '__main__':
	ctrl = HVACPIDController()

	while True:
		time.sleep(1)
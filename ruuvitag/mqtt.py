import logging
import paho.mqtt.publish as publish

class MQTTClient(object):
	def  __init__(self, client_id, address, port):
		self.client_id = client_id
		self.address = address
		self.port = port

	def publishMany(self, messages):
		publish.multiple(messages, self.address, self.port)

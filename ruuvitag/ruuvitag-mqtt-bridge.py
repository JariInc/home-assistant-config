import os
import json
import logging
from threading import Timer
from mqtt import MQTTClient
from ruuvitag import Ruuvitag
from dotenv import load_dotenv

load_dotenv()

def handleRuuvitag(data):
	(mac, measurements) = data
	mqtt_topic = 'ruuvitag/' + mac.replace(':', '')
	logger.info("Publishing %s", mac)
	mqtt_client.publish(mqtt_topic, json.dumps(measurements))

def publishMeasurements(mqtt_client, ruuvi, macs):
	logger.info("Publishing measurements")
	for mac in macs:
		measurement = ruuvi.getMeasurement(mac)
		if measurement:
			mqtt_topic = 'ruuvitag/' + mac.replace(':', '')
			logger.info("Publishing %s", mac)
			mqtt_client.publish(mqtt_topic, json.dumps(measurements))

if __name__ == '__main__':
	logger = logging.getLogger('ruuvitag-mqtt-bridge')
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	logger.info("Starting app")

	interval = int(os.getenv('INTERVAL'))

	mqtt = MQTTClient(os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_BROKER_HOST'), int(os.getenv('MQTT_BROKER_PORT')))

	ruuvitag_macs = os.getenv('RUUVITAG_MACS').split(',')
	ruuvi = Ruuvitag(ruuvitag_macs, interval)

	logger.info("Listening ruuvitags %s", ruuvitag_macs);
	logger.info("Publishing data every %d seconds", interval);

	#t = Timer(interval, publishMeasurements, (mqtt_client, ruuvi, ruuvitag_macs))
	#t.start()

	while True:
		logger.info("Getting data from ruuvitags")
		ruuvi.update()

		messages = []
		for mac in ruuvitag_macs:
			measurement = ruuvi.getMeasurement(mac)
			if measurement:
				logger.info("Building message for %s", mac)
				messages.append({
					'topic': 'ruuvitag/' + mac.replace(':', ''),
					'payload': json.dumps(measurement),
					'qos': 0,
					'retain': True,
				})

		if len(messages) > 0:
			logger.info("Publishing measurements")
			mqtt.publishMany(messages)

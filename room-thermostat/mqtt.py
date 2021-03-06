import logging
import paho.mqtt.client as mqtt

class MQTTClient(object):
    client = None
    client_id = None
    host = None
    port = 1883
    keepalive = 15

    def __init__(self, client_id, host, port=1883):
        self.client_id = client_id
        self.host = host
        self.port = port

        self.client = mqtt.Client(self.client_id)
        self.client.disable_logger()

    def connect(self):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()

    def subscribe(self, topic, callback=None, qos=2):
        self.client.subscribe(topic, qos)

        if callback:
            self.client.message_callback_add(topic, callback)

    def publish(self, topic, message, qos=2, retain=True):
        self.client.publish(topic, message, qos, retain)

    def will(self, topic, message, qos=2, retain=True):
        self.client.will_set(topic, message, qos, retain)

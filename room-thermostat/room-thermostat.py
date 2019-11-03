import logging
import time
import json
import re
from mqtt import MQTTClient
from config import Config
from hass import HomeAssistant

class RoomThermostat(object):
    mqtt = None
    config = None
    hass = None
    mode = {}
    target = {}
    temp = {}

    def __init__(self):
        self.logger = logging.getLogger('room-thermostat')
        self.logger.info('Starting room thermostat')

        # Config
        self.config = Config('./config.yaml')

        # HomeAssistant
        self.hass = HomeAssistant()

        # MQTT
        self.mqtt = MQTTClient(self.config.mqtt['client_id'], self.config.mqtt['host'], self.config.mqtt['port'])
        self.mqtt.will(f"roomthermostat/availability", 'offline')
        self.mqtt.connect()
        self.publishAvailable()

        for room in self.config.rooms:
            self.subscribeRoom(room)

        self.publishAutoDiscovery()

    def subscribeRoom(self, room):
        # temperature_command_topic
        self.mqtt.subscribe(f"roomthermostat/{room['name_snakecase']}/temperature/set", self.temperatureCommand)

        # mode_command_topic
        self.mqtt.subscribe(f"roomthermostat/{room['name_snakecase']}/mode/set", self.modeCommand)

        # measurement_topic
        self.mqtt.subscribe(room['measurement_topic'], self.measurement)

    def publishAutoDiscovery(self):
        for room in self.config.rooms:
            self.logger.info(f"Publishing auto discovery for '{room['name']}'")
            self.mqtt.publish(*self.hass.buildDiscoveryMessage(room))

    def publishAvailable(self):
        self.logger.info(f"Publishing availability")
        self.mqtt.publish(f"roomthermostat/availability", 'online')

    def publishMode(self, name, mode):
        self.logger.info(f"Publishing mode for '{name}'")
        self.mqtt.publish(f"roomthermostat/{name}/mode", mode)

    def publishTarget(self, name, temperature):
        self.logger.info(f"Publishing target temperature for '{name}'")
        self.mqtt.publish(f"roomthermostat/{name}/temperature", str(temperature))

    def publishTemperature(self, name, temperature):
        self.logger.info(f"Publishing temperature for '{name}'")
        self.mqtt.publish(f"roomthermostat/{name}/current_temperature", str(temperature))

    def publishEnableHeating(self, room):
        self.logger.info(f"Publishing enable heating for '{room['name_snakecase']}'")
        self.mqtt.publish(room['control_topic'], "on")
        self.publishAction(room['name_snakecase'], self.mode[room['name_snakecase']], True)

    def publishDisableHeating(self, room):
        self.logger.info(f"Publishing disable heating for '{room['name_snakecase']}'")
        self.mqtt.publish(room['control_topic'], "off")
        self.publishAction(room['name_snakecase'], self.mode[room['name_snakecase']], False)

    def publishAction(self, name, mode, relayOn):
        if mode == 'off':
            action = 'off'
        elif relayOn == True:
            action = 'heating'
        elif relayOn == False:
            action = 'idle'
        else:
            self.logger.error(f"Cannot publish action for '{name}', mode: '{mode}', relayOn: '{relayOn}'")
            return

        self.logger.info(f"Publishing action for '{name}'")
        self.mqtt.publish(f"roomthermostat/{name}/action", action)

    def temperatureCommand(self, client, userdata, message):
        name = self._parseRoomNameFromTopic(message.topic)
        temperature = float(message.payload.decode('utf-8'))

        if temperature >= 15 and temperature <= 25:
            self.logger.info(f"Received target temperature '{temperature}' for '{name}'")
            self.target[name] = temperature
            self.publishTarget(name, self.target[name])
            self.iterateRoom(self._findRoomByName(name))
        else:
            self.logger.error(f"Invalid target temperature '{temperature}' for '{name}'")

    def modeCommand(self, client, userdata, message):
        name = self._parseRoomNameFromTopic(message.topic)
        mode = message.payload.decode('utf-8')

        if mode in ['heat', 'off']:
            self.logger.info(f"Received mode '{mode}' for '{name}'")
            self.mode[name] = mode
            self.publishMode(name, self.mode[name])
            self.iterateRoom(self._findRoomByName(name))
        else:
            self.logger.error(f"Unknown mode '{mode}' for '{name}'")

    def measurement(self, client, userdata, message):
        topic = message.topic
        payload_json = json.loads(message.payload.decode('utf-8'))
        newMeasurement = float(payload_json['temperature'])

        for room in self.config.rooms:
            name = room['name_snakecase']

            if room['measurement_topic'] == topic and (name not in self.temp or self.temp[name] != newMeasurement):
                self.logger.info(f"Received new measurement '{newMeasurement}' for '{name}'")
                self.temp[name] = newMeasurement
                self.iterateRoom(room)

    def _parseRoomNameFromTopic(self, topic):
        pattern = re.compile('roomthermostat/([a-z0-9_-]+)/(.+)/set')
        match = pattern.match(topic)

        return match.group(1)

    def _findRoomByName(self, name):
        for room in self.config.rooms:
            if room['name'] == name or room['name_snakecase'] == name:
                return room

        return None

    def iterateRoom(self, room):
        name = room['name_snakecase']

        # initialize with home temperature
        if not name in self.target:
            self.target[name] = room['temperatures']['home']
            self.publishTarget(name, self.target[name])

        if not name in self.temp or not name in self.mode:
            return
        else:
            self.publishTemperature(name, self.temp[name])
            diff = self.temp[name] - self.target[name]
            mode = self.mode[name]

            if mode != 'heat':
                # turn relay off
                self.logger.info(f"Turning off heating in '{room['name']}', mode: '{mode}' diff: {diff:.2f}")
                self.publishDisableHeating(room)
            elif diff > 1.0:
                # turn relay off
                self.logger.info(f"Turning off heating in '{room['name']}', mode: '{mode}' diff: {diff:.2f}")
                self.publishDisableHeating(room)
            elif diff < 1.0:
                # turn relay on
                self.logger.info(f"Turning on heating in '{room['name']}', mode: '{mode}' diff: {diff:.2f}")
                self.publishEnableHeating(room)
            else:
                # keep current relay state
                return

if __name__ == '__main__':
    logger = logging.getLogger('room-thermostat')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    app = RoomThermostat()

    while True:
        time.sleep(1)

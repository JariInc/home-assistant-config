import logging
import stringcase
import json
from hashlib import sha1

class HomeAssistant(object):
    def __init__(self):
        self.logger = logging.getLogger('room-thermostat')

    def buildDiscoveryMessage(self, room, discoveryPrefix='homeassistant'):
        snakeCaseName = stringcase.snakecase(room['name'])
        uniqueId = sha1(snakeCaseName.encode()).hexdigest()

        topic = f"{discoveryPrefix}/climate/{snakeCaseName}/config"
        message = {
            'platform': 'mqtt',
            'name': room['name'],
            'unique_id': uniqueId,
            'min_temp': 15,
            'max_temp': 25,
            'temp_step': 0.1,
            'precision': 0.1,
            'send_if_off': True,
            'retain': True,
            'qos': 2,
            'modes': ['heat', 'off'],
            'current_temperature_topic': f"roomthermostat/{snakeCaseName}/current_temperature",
            'temperature_command_topic': f"roomthermostat/{snakeCaseName}/temperature/set",
            'temperature_state_topic': f"roomthermostat/{snakeCaseName}/temperature",
            'mode_command_topic': f"roomthermostat/{snakeCaseName}/mode/set",
            'mode_state_topic': f"roomthermostat/{snakeCaseName}/mode",
            'action_topic': f"roomthermostat/{snakeCaseName}/action",
            'availability_topic': f"roomthermostat/availability",
        }
        qos = 2
        retain = True

        return (topic, json.dumps(message), qos, retain)

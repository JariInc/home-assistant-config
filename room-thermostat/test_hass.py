from hass import HomeAssistant
import json

def test_autoDiscoveryMessage():
    ha = HomeAssistant()

    room = {
        'name': 'Auto discovery',
        'measurement_topic': 'foo/bar',
        'control_topic': 'fizz/buzz',
        'temperatures': {
            'home': 21,
            'away': 17,
        },
    }

    discoveryPrefix = 'discoprefix'

    (topic, message, qos, retain) = ha.buildDiscoveryMessage(room, discoveryPrefix)

    exptectedMessage = {
        'platform': 'mqtt',
        'name': 'Auto discovery',
        'unique_id': 'bb12fb05be004ab48f3725d3b08a3e0651476f83',
        'min_temp': 15,
        'max_temp': 25,
        'temp_step': 0.1,
        'precision': 0.1,
        'send_if_off': True,
        'retain': True,
        'qos': 2,
        'modes': ['heat', 'off'],
        'current_temperature_topic': 'roomthermostat/auto_discovery/current_temperature',
        'temperature_command_topic': 'roomthermostat/auto_discovery/temperature/set',
        'temperature_state_topic': 'roomthermostat/auto_discovery/temperature',
        'mode_command_topic': 'roomthermostat/auto_discovery/mode/set',
        'mode_state_topic': 'roomthermostat/auto_discovery/mode',
        'availability_topic': 'roomthermostat/availability',
        'action_topic': f"roomthermostat/auto_discovery/action",
    }

    assert topic == 'discoprefix/climate/auto_discovery/config'
    assert json.loads(message) == exptectedMessage
    assert qos == 2
    assert retain == True

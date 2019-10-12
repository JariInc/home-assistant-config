import logging
import time
import os
import json
from mqtt import MQTTClient
from temp import Temp
from fan import Fan
from power import Power
from math import floor
from util import Util
from config import Config
from dotenv import load_dotenv
from state import State

load_dotenv()

class HVACPIDController(object):
    logger = None
    mqtt = None
    temp = None
    fan = None
    power = None
    config = None
    state = None

    temp_outdoors = 0

    mode = 'auto'
    manual = False
    control_enable = False
    hvac_state = {}

    def __init__(self):
        self.logger = logging.getLogger('hvac-pid')
        self.logger.info('Starting hvac-pid')

        self.config = Config()
        self.util = Util()

        # PID options
        pid_options = self.config.getPIDOptions(self.mode)
        temp_options = self.config.getTempOptions(self.mode)

        # Temp
        self.temp = Temp(**{**temp_options, **pid_options})

        # Fan
        self.fan = Fan()

        # Power
        self.power = Power()

        # Occupancy state
        self.state = State(**self.config.getStateOptions())

        # MQTT
        self.topic_prefix = os.getenv('MQTT_PID_TOPIC_PREFIX')
        self.mqtt = MQTTClient(os.getenv('MQTT_CLIENT_ID'), os.getenv('MQTT_BROKER_HOST'))
        self.mqtt.connect()

        # subscribe
        self.mqtt.subscribe(os.getenv('MQTT_TEMP_TOPIC'), 0, self.temp_update_callback)
        self.mqtt.subscribe(os.getenv('MQTT_TEMP_OUTDOORS_TOPIC'), 0, self.temp_outdoors_update_callback)
        self.mqtt.subscribe(os.getenv('MQTT_HVAC_STATE_TOPIC'), 0, self.hvac_callback)
        self.mqtt.subscribe(self.topic_prefix + '/mode/set', 0, self.set_mode)
        self.mqtt.subscribe(self.topic_prefix + '/temperature/set', 0, self.set_temp)
        self.mqtt.subscribe(self.topic_prefix + '/fan/set', 0, self.set_fan)
        self.mqtt.subscribe(os.getenv('MQTT_HVAC_OCCUPANCY_STATE_TOPIC'), 0, self.set_occupancy_state)

        self.logger.info('MQTT connected')

        self.publish_temp()
        self.publish_mode()
        self.publish_fan()

        # wait a bit before enabling control
        time.sleep(3)
        self.control_enable = True

    def iterate(self):
        if self.manual:
            self.logger.info('Manual mode, skipping PID iteration')
        else:
            # temp hax
            # limit min temp when outdoors is < -10
            if self.temp_outdoors < -10:
                self.temp.setLimits(floor(self.temp.temp_request), self.config.getSetTempMax())
                self.logger.debug('Limiting min temp to %g when outdoor temp is %g', self.temp.temp_min, self.temp_outdoors)
            else:
                self.temp.setLimits(self.config.getSetTempMin(), self.config.getSetTempMax())

            compensated_request_temp = self.state.compensateRequestTemp(self.temp.temp_request, self.temp_outdoors)
            self.temp.iteratePID(compensated_request_temp)
            self.fan.calculate(self.temp.pid_offset, self.mode)
            self.power.calculate(self.temp.temp_request, self.temp.temp_measure, self.mode, self.temp_outdoors)
            if not self.power.state:
                self.temp.pid.reset()
            self.publish_state()

    def temp_update_callback(self, client, userdata, message):
        payload_json = json.loads(message.payload.decode('utf-8'))

        if self.mode == 'cool':
            dew_point = self.util.dewPoint(payload_json['temperature'], payload_json['humidity'])
            self.temp.setMeasurement(round(dew_point, 2), payload_json['temperature'])
        else:
            self.temp.setMeasurement(payload_json['temperature'], payload_json['temperature'])

    def temp_outdoors_update_callback(self, client, userdata, message):
        payload_json = json.loads(message.payload.decode('utf-8'))
        self.temp_outdoors = float(payload_json['temperature'])

    def hvac_callback(self, client, userdata, message):
        payload_json = json.loads(message.payload.decode('utf-8'))
        self.logger.info('Received hvac state change %s', payload_json)
        self.hvac_state = payload_json

    def setHVAC(self):
        if self.control_enable:
            topic = os.getenv('MQTT_HVAC_TOPIC')
            new_state = {
                'power': self.power.state,
                'mode': self.mode.upper(),
                'temperature': self.temp.temp_set,
                'fan': self.fan.speed,
            }

            is_state_changed = (new_state['power'] and self.hvac_state != new_state)
            is_power_state_changed = (self.hvac_state and new_state['power'] != self.hvac_state['power'])
            old_state_doesnt_exists = (not self.hvac_state)

            if is_state_changed or is_power_state_changed or old_state_doesnt_exists:
                message = json.dumps(new_state)

                self.logger.debug('Controlling HVAC with command %s', message)
                self.mqtt.publish(topic, message, 1)
            else:
                self.logger.debug('HVAC state unchanged %s', self.hvac_state)
        else:
            self.logger.debug('Controlling HVAC disabled')

    def set_mode(self, client, userdata, message):
        mode = message.payload.decode('utf-8')
        previous_mode = self.mode

        # reset PID if switching between modes
        if previous_mode != mode:
            pid_options = self.config.getPIDOptions(mode)
            temp_options = self.config.getTempOptions(mode)
            self.temp = Temp(**{**temp_options, **pid_options})
            self.temp.temp_set = self.temp.temp_measure

        if mode == 'off':
            self.manual = True
            self.mode = 'auto'
            self.power.state = False
            self.logger.info('Set mode to off')
        if mode == 'manual':
            self.manual = True
            self.power.state = True
            self.mode = 'auto'
            self.temp.temp_set = self.temp.temp_request
            self.logger.info('Set mode to manual')
        elif mode == 'heat':
            self.manual = False
            self.mode = mode
            self.logger.info('Set mode to %s', self.mode)
        elif mode == 'cool':
            self.manual = False
            self.mode = mode
            self.logger.info('Set mode to %s', self.mode)

        self.publish_mode()
        self.setHVAC()

    def publish_mode(self):
        if not self.control_enable:
            return

        topic = self.topic_prefix + '/mode/state'

        if self.manual:
            if self.power.state == False:
                mode = 'off'
            else:
                mode = 'manual'
        elif self.mode == 'auto':
            mode = 'manual'
        else:
            mode = self.mode

        self.mqtt.publish(topic, mode, 1, True)

    def set_temp(self, client, userdata, message):
        temp = round(float(message.payload.decode('utf-8')), 2)

        if temp >= float(os.getenv('REQUEST_MIN_TEMP', 0)) and temp <= float(os.getenv('REQUEST_MAX_TEMP', 100)):
            self.temp.setRequest(temp)

            if self.manual:
                self.temp.temp_set = self.temp.temp_request
            else:
                self.temp.pid.reset()

            self.publish_temp()
            self.setHVAC()

    def publish_temp(self):
        if not self.control_enable:
            return

        self.mqtt.publish(self.topic_prefix + '/temperature/state', self.temp.temp_request, 1, True)
        self.mqtt.publish(self.topic_prefix + '/measured_temperature', self.temp.temp_measure, 1, True)

    def set_fan(self, client, userdata, message):
        fan = message.payload.decode('utf-8')

        if fan != "auto":
            fan_int = int(fan)

            if self.manual and fan_int >= 1 and fan_int <= 5:
                self.fan.speed = fan_int
                self.publish_fan()
                self.setHVAC()
                self.logger.info('Manually set fan speed to %s/5', self.fan.speed)

    def publish_fan(self):
        if not self.control_enable:
            return

        topic = self.topic_prefix + '/fan/state'

        if self.manual:
            fan = self.fan.speed
        else:
            fan = 'auto'

        self.mqtt.publish(topic, fan, 1, True)

    def publish_state(self):
        if not self.control_enable:
            return

        topic = os.getenv('MQTT_PID_TOPIC_PREFIX') + '/state'
        message = json.dumps({
            'mode': self.mode,
            'manual': self.manual,
            'temperature_request': float(self.temp.temp_request),
            'temperature_set': float(self.temp.temp_set),
            'temperature_measure': float(self.temp.temp_measure),
            'temperature_error': float(self.temp.pid.previous_error),
            'fan': int(self.fan.speed if self.power.state else 0),
            'power': self.power.state,
            'Kp': float(self.temp.pid.Kp),
            'Ki': float(self.temp.pid.Ki),
            'Kd': float(self.temp.pid.Kd),
            'integral': float(self.temp.pid.integral),
            'integral_max': float(self.temp.pid.integral_max),
            'pid_output': float(self.temp.pid.output)
        })
        self.mqtt.publish(topic, message, 1)

    def set_occupancy_state(self, client, userdata, message):
        state = message.payload.decode('utf-8')
        self.state.setState(state)
        self.logger.info('Setting occupancy state to %s', self.state.state)
        self.temp.pid.scaleIntegral()

if __name__ == '__main__':
    logger = logging.getLogger('hvac-pid')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    ctrl = HVACPIDController()

    while True:
        time.sleep(ctrl.config.getWaitTime(ctrl.mode))

        if not ctrl.manual:
            ctrl.iterate()
            ctrl.setHVAC()
            ctrl.publish_mode()
            ctrl.publish_fan()

        ctrl.publish_temp()

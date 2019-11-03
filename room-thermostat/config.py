import yaml
import logging
import stringcase
import os

class Config(object):
    def __init__(self, configFile):
        self.logger = logging.getLogger('room-thermostat')

        configFileFullPath = os.path.abspath(configFile)

        self.logger.info(f"Parsing config file {configFileFullPath}")

        with open(configFileFullPath, 'r') as stream:
            try:
                self.parseYaml(yaml.safe_load(stream))
            except yaml.YAMLError as e:
                self.logger.info(f"YAML parsing failed: {e}")

    def parseYaml(self, yaml):
        self.interval = yaml['interval']
        self.mqtt = yaml['mqtt']
        self.rooms = yaml['rooms']

        for room in self.rooms:
            room['name_snakecase'] = stringcase.snakecase(room['name'])

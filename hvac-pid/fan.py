import logging

class Fan(object):
    # state
    speed = 3

    def __init__(self):
        self.logger = logging.getLogger('hvac-pid.fan')

    def calculate(self, temp_offset, mode):
        is_heat = mode == 'heat'

        if is_heat:
            self._heating(temp_offset)
        else:
            self._cooling(temp_offset)

        self.logger.info('Fan speed is %s/5 in %s mode', self.speed, mode)

    def _heating(self, offset):
        if offset < -3:
            self.speed = 1
        elif offset < -2:
            self.speed = 2
        elif offset < 0:
            self.speed = 3
        elif offset < 1:
            self.speed = 4
        else:
            self.speed = 5

    def _cooling(self, offset):
        if offset < -3:
            self.speed = 5
        elif offset < -2:
            self.speed = 4
        elif offset < -1:
            self.speed = 3
        elif offset < 0:
            self.speed = 2
        else:
            self.speed = 1

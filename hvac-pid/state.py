import logging

class State(object):
    state = 'home'
    mode = None

    temps = {
      'heat': {
        'home': None,
        'away': 19,
        'sleep': 19,
      },
      'cool': {
        'home': None,
        'away': 15,
        'sleep': None,
      }
    }

    compensate = {
      'home': False,
      'away': True,
      'sleep': True,
    }

    compensation_lower_limit = 0
    compensation_upper_limit = 0

    def __init__(self, upper_limit, lower_limit):
        self.logger = logging.getLogger('hvac-pid.state')
        self.compensation_upper_limit = upper_limit
        self.compensation_lower_limit = lower_limit

    def setState(self, state):
        if state in self.compensate.keys():
            self.state = state

    def setMode(self, mode):
      self.mode = mode

    def compensateRequestTemp(self, request_temp, outside_temp):
        compensate = self.compensate[self.state]

        if compensate and self.mode in self.temps and self.state in self.temps[self.mode]:
            compensatedValue = ((request_temp - self.temps[self.mode][self.state]) * self.getScalingFactor(outside_temp)) + self.temps[self.mode][self.state]
            self.logger.info('compensate request temp from %g to %g', request_temp, compensatedValue)
            return compensatedValue
        else:
            return request_temp

    def getScalingFactor(self, outside_temp):
        if outside_temp > self.compensation_upper_limit:
            return 0.0
        elif outside_temp > self.compensation_lower_limit:
            return (1/self.compensation_lower_limit) * outside_temp
        else:
            return 1.0

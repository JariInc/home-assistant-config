import logging

class State(object):
    state = 'home'

    temps = {
      'home': None,
      'away': 19,
      'sleep': 19,
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

    def compensateRequestTemp(self, request_temp, outside_temp):
        compensate = self.compensate[self.state]

        if compensate:
            return ((request_temp - self.temps[self.state]) * self.getScalingFactor(outside_temp)) + self.temps[self.state]
        else:
            return request_temp

    def getScalingFactor(self, outside_temp):
        if outside_temp > self.compensation_upper_limit:
            return 0.0
        elif outside_temp > self.compensation_lower_limit:
            return (1/self.compensation_lower_limit) * outside_temp
        else:
            return 1.0

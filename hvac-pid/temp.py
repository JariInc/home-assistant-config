import logging
from pid import PID

class Temp(object):
    logger = None
    pid = None

    # state
    temp_request = 21
    temp_measure = 21
    temp_set = 21

    temp_min = -100
    temp_max = 100

    def __init__(self, temp_max, temp_min, **pid_options):
        self.logger = logging.getLogger('hvac-pid.temp')
        self.pid = PID(**{
            **pid_options, 
            'max_output': temp_max, 
            'min_output': temp_min,
        });

        self.temp_max = temp_max
        self.temp_min = temp_min

    def setMeasurement(self, temp_measure):
        self.temp_measure = temp_measure
        self.logger.info('Measured temperature is %s', self.temp_measure)

    def setRequest(self, temp_request):
        self.temp_request = temp_request
        self.logger.info('Requested temperature is %s', self.temp_request)

    def iteratePID(self):
        pid_output = self.pid.iterate(self.temp_request, self.temp_measure)
        self.setTemperature(pid_output)

    def setTemperature(self, temp):
        # allow only +-1 degree change at once
        old_value = self.temp_set
        set_value = int(round(min(old_value + 1, max(old_value - 1, temp))))
        self.temp_set = int(round(min(self.temp_max, max(self.temp_min, set_value))))
        self.logger.info('Set temperature is %s', self.temp_set)

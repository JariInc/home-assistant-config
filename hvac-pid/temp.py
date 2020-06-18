import logging
from pid import PID

class Temp(object):
    logger = None
    pid = None

    # state
    temp_request = 21
    temp_measure = 21
    temp_set = 21
    temp_absolute = 21
    pid_offset = 0
    pid_result = None

    temp_min = -100
    temp_max = 100

    mode = 'heat'

    def __init__(self, temp_max, temp_min, mode, **pid_options):
        self.logger = logging.getLogger('hvac-pid.temp')
        self.pid = PID(**{
            **pid_options,
            'max_output': temp_max,
            'min_output': temp_min,
        });

        self.temp_max = temp_max
        self.temp_min = temp_min
        self.mode = mode

    def setMeasurement(self, temp_measure, temp_absolute):
        self.temp_measure = temp_measure
        self.temp_absolute = temp_absolute
        self.logger.info('Measured temperature is %s absolute temperature is %s', self.temp_measure, self.temp_absolute)

    def setRequest(self, temp_request):
        self.temp_request = temp_request
        self.logger.info('Set requested temperature to %s', self.temp_request)

    def iteratePID(self, temp_request_override = None):
        if not self.pid_result:
            self.pid_result = self.temp_absolute

        effective_temp_request = temp_request_override if temp_request_override != None else self.temp_request

        if self.mode == 'cool':
            self.pid.setLimits(0, 30)
        else:
            self.pid.setLimits(self.temp_min, self.temp_max)

        self.pid_offset = self.pid.iterate(effective_temp_request, self.temp_measure)
        self.pid_result += self.pid_offset

        if self.pid_result < self.temp_min:
            self.pid_result = self.temp_min
        elif self.pid_result > self.temp_max:
            self.pid_result = self.temp_max

        self.setTemperature(self.pid_result)

    def setTemperature(self, temp):
        max_temp = self.temp_absolute + 3.0
        min_temp = self.temp_min 
        self.logger.debug('Set temperature limits [%g, %g] input %g', max_temp, min_temp, temp)

        self.temp_set = int(round(min(max_temp, max(min_temp, temp))))
        self.logger.info('Set temperature is %s', self.temp_set)

    def setLimits(self, temp_min, temp_max):
        self.temp_min = temp_min
        self.temp_max = temp_max

    def reset(self):
        self.logger.info('Reset temps')
        self.pid.reset()
        self.pid_result = self.temp_absolute

import logging
from pid import PID

class Temp(object):
    logger = None
    pid = None

    # state
    temp_request = 21
    temp_measure = 21
    temp_set = 21

    def __init__(self, **pid_options):
        self.logger = logging.getLogger('hvac-pid.temp')
        self.pid = PID(**pid_options);

    def setMeasurement(self, temp_measure):
        self.temp_measure = temp_measure
        self.logger.info('Measured temperature is %s', self.temp_measure)

    def setRequest(self, temp_request):
        self.temp_request = temp_request
        self.logger.info('Measured temperature is %s', self.temp_request)

    def iteratePID(self):
        pid_output = self.pid.iterate(self.temp_request, self.temp_measure)
        self.temp_set = int(round(min(30, max(17, pid_output))))
        self.logger.info('Set temperature is %s', self.temp_set)
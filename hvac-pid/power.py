import logging

class Power(object):
    # state
    state = True
    threshold = 0
    hysteresis = 0
    threshold_params = {'a': 0.01, 'b': 0, 'c': 1}

    def __init__(self, threshold=1.0, hysteresis=0.5):
        self.logger = logging.getLogger('hvac-pid.power')
        self.threshold = threshold
        self.hysteresis = hysteresis

    def calculate(self, temp_request, temp_measure, temp_set, mode, temp_outdoors = 0):
        is_heat = mode == 'heat'

        if is_heat:
            threshold = temp_request + self._threshold(temp_outdoors, self.threshold_params)
            self.state = not self._hysteresis(threshold, temp_measure, not self.state, True)
        else:
            threshold = temp_request - self.threshold
            self.state = not self._hysteresis(threshold, temp_measure, not self.state, False)

        self.logger.debug('Power off threshold is %g before hysteresis', threshold)
        self.logger.info('Power is %s', self.state)


    def _hysteresis(self, threshold, value, crossed_threshold, direction):
        lower_threshold = threshold - (self.hysteresis / 2)
        upper_threshold = threshold + (self.hysteresis / 2)

        self.logger.debug("Thresholds %s (%s/%s) crossed %s value %s", threshold, lower_threshold, upper_threshold, crossed_threshold, value)

        if direction:
            if crossed_threshold:
                return (value > lower_threshold)
            else:
                return (value > upper_threshold)
        else:
            if crossed_threshold:
                return (value < upper_threshold)
            else:
                return (value < lower_threshold)

    def _threshold(self, temp_outdoors, params):
        if temp_outdoors >= 0:
            return 1.0
        else:
            # parabola
            return params['a'] * pow(temp_outdoors, 2) + params['b'] * temp_outdoors + params['c']
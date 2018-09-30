import logging

class Power(object):
	# state
	state = True

	def __init__(self, threshold=1.0, hysteresis=0.5):
		self.logger = logging.getLogger('hvac-pid.power')

	def calculate(self, temp_request, temp_measure, mode):
		is_heat = mode == 'heat'

		if is_heat:
			threshold = temp_request + 1.0
			self.state = not self._hysteresis(threshold, temp_measure, 0.5, not self.state, True)
		else:
			threshold = temp_request - 1.0
			self.state = not self._hysteresis(threshold, temp_measure, 0.5, not self.state, False)

		self.logger.info('Power is %s', self.state)


	def _hysteresis(self, threshold, value, hysteresis, crossed_threshold, direction):
		lower_threshold = threshold - (hysteresis / 2)
		upper_threshold = threshold + (hysteresis / 2)

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

import logging

class Fan(object):
	# state
	speed = 3

	def __init__(self):
		self.logger = logging.getLogger('hvac-pid.fan')

	def calculate(self, temp_error, mode):
		error_abs = abs(temp_error)
		is_heat = mode == 'heat'

		if is_heat:
			self._heating(temp_error)
		else:
			self._cooling(temp_error)

		self.logger.info('Fan speed is %s/5 in %s mode', self.speed, mode)

	def _heating(self, error):
		if error < -2:
			self.speed = 1
		elif error < -1:
			self.speed = 2
		elif error < 2:
			self.speed = 3
		elif error < 3:
			self.speed = 4
		else:
			self.speed = 5

	def _cooling(self, error):
		if error < -2:
			self.speed = 5
		elif error < -1:
			self.speed = 4
		elif error < 2:
			self.speed = 3
		elif error < 3:
			self.speed = 2
		else:
			self.speed = 1
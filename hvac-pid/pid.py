import logging
from time import monotonic

class PID(object):
	logger = None

	previous_error = 0
	integral = 0
	integral_max = 0
	iteration_ts = 0
	Kp = 1
	Ki = 1
	Kd = 1
	output = 0

	def __init__(self, Kp, Ki, Kd, integral_max_effect):
		self.logger = logging.getLogger('hvac-pid.pid')

		self.Kp = Kp
		self.Ki = Ki
		self.Kd = Kd

		self.logger.info("Initialized with Kp=%g, Ki=%g, Kd=%g", self.Kp, self.Ki, self.Kd)

		# allow integral to control at max integral_max_effect degrees
		self.integral_max = integral_max_effect / self.Ki
		self.iteration_ts = monotonic()
		
	def reset(self):
		self.previous_error = 0
		self.integral = 0
		self.iteration_ts = monotonic()
		self.logger.info("PID reseted")

	def iterate(self, set_point, measurement):
		ts = monotonic()

		dt = (ts - self.iteration_ts) / 60
		self.logger.debug("dt: %g min", dt)
		
		error = set_point - measurement
		self.logger.debug("error: %g - %g = %g", set_point, measurement, error)
		
		new_integral = self.integral + (error * dt)
		self.logger.debug("integral: %g + (%g * %g) = %g", self.integral, error, dt, new_integral)

		if abs(new_integral) > self.integral_max:
			new_integral = 	(new_integral / abs(new_integral)) * self.integral_max
			self.logger.info("integral clamped to: %g", new_integral)	
		
		derivative = (error - self.previous_error) / dt
		self.logger.debug("derivative: (%g - %g) / %g = %g", error, self.previous_error, dt, derivative)		
		
		output = self.Kp * error + self.Ki * new_integral + self.Kd * derivative
		self.logger.debug("output: %g * %g + %g * %g + %g * %g = %g", self.Kp, error, self.Ki, new_integral, self.Kd, derivative, output)		

		self.integral = new_integral
		self.iteration_ts = ts
		self.previous_error = error

		self.output = set_point + output

		return self.output
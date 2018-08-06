import logging
from time import monotonic

class PID(object):
	logger = None

	previous_error = 0
	integral = 0
	iteration_ts = 0
	Kp = 1
	Ki = 1
	Kd = 1

	def __init__(self, Kp, Ki, Kd):
		self.logger = logging.getLogger('hvac-pid.pid')

		self.Kp = Kp
		self.Ki = Ki
		self.Kd = Kd

		self.logger.info("Initialized with Kp=%g, Ki=%g, Kd=%g", self.Kp, self.Ki, self.Kd)

		self.iteration_ts = monotonic()

	def iterate(self, set_point, measurement):
		ts = monotonic()

		dt = ts - self.iteration_ts
		self.logger.debug("dt: %g", dt)
		
		error = set_point - measurement
		self.logger.debug("error: %g - %g = %g", set_point, measurement, error)
		
		new_integral = self.integral + (error * dt)
		self.logger.debug("integral: %g + (%g * %g) = %g", self.integral, error, dt, new_integral)		
		
		derivative = (error - self.previous_error) / dt
		self.logger.debug("derivative: (%g - %g) / %g = %g", error, self.previous_error, dt, derivative)		
		
		output = self.Kp * error + self.Ki * new_integral + self.Kd * derivative
		self.logger.debug("output: %g * %g + %g * %g + %g * %g = %g", self.Kp, error, self.Ki, new_integral, self.Kd, derivative, output)		

		self.integral = new_integral
		self.iteration_ts = ts
		self.previous_error = error

		return set_point + output
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

    def __init__(self, Kp, Ki, Kd, min_output, max_output):
        self.logger = logging.getLogger('hvac-pid.pid')

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.logger.info("Constants: Kp=%g, Ki=%g, Kd=%g", self.Kp, self.Ki, self.Kd)

        self.min_output = min_output
        self.max_output = max_output
        self.logger.info("Output limits [%g, %g]", self.min_output, self.max_output)

        self.iteration_ts = monotonic()
        
    def reset(self):
        self.previous_error = 0
        self.integral = 0
        self.iteration_ts = monotonic()
        self.logger.info("PID reseted")

    def iterate(self, set_point, measurement, ts=None):
        if not ts:
            ts = monotonic()

        dt = (ts - self.iteration_ts) / 60
        self.logger.debug("dt: %g min", dt)
        
        error = set_point - measurement
        self.logger.debug("error: %g - %g = %g", set_point, measurement, error)
        
        new_integral = self.integral + (error * dt)
        self.logger.debug("integral: %g + (%g * %g) = %g", self.integral, error, dt, new_integral)
        
        derivative = (error - self.previous_error) / dt
        self.logger.debug("derivative: (%g - %g) / %g = %g", error, self.previous_error, dt, derivative)        

        # clamp intergral to max
        max_integral = self.max_integral(set_point, error, derivative)
        new_integral = max_integral if new_integral > max_integral else new_integral
        
        # clanmp integral to min
        min_integral = self.min_integral(set_point, error, derivative)
        new_integral = min_integral if new_integral < min_integral else new_integral

        self.logger.debug("integral limits: [%g, %g]", min_integral, max_integral)

        output = self.Kp * error + self.Ki * new_integral + self.Kd * derivative
        self.logger.debug("output: %g * %g + %g * %g + %g * %g = %g", self.Kp, error, self.Ki, new_integral, self.Kd, derivative, output)       

        self.integral = new_integral
        self.iteration_ts = ts
        self.previous_error = error

        self.output = set_point + output

        return self.output

    def max_integral(self, set_point, proportional, derivative):
        return (self.max_output - set_point - (self.Kp * proportional) - (self.Kd * derivative)) / self.Ki

    def min_integral(self, set_point, proportional, derivative):
        return (self.min_output - set_point - (self.Kp * proportional) - (self.Kd * derivative)) / self.Ki
from pid import PID

def test_min_integral():
    pid = PID(3, 0.2, 0, 17, 30)

    min_value = pid.min_integral(21, -0.51, -1.32352)

    assert min_value < 0

def test_integral_min_limit():
    pid = PID(3, 0.2, 0, 17, 30)
    pid.iteration_ts = 0

    output = pid.iterate(21, 21.51, 0.385337*60)

    assert output > -2 and output < -1

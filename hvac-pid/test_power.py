from power import Power

def test_heating_power_on():
    state = True
    request = 21.0
    threshold = 1.0
    hysteresis = 0.5

    power = Power(threshold, hysteresis)

    #  above request, below threshold => power on
    power.state = state
    power.calculate(request, request + (threshold / 2), 'heat')
    assert power.state == True

    #  above request, above threshold, below hysteresis => power on
    power.state = state
    power.calculate(request, request + threshold + (hysteresis / 2), 'heat')
    assert power.state == True

    #  above request, above threshold, above hysteresis => power off
    power.state = state
    power.calculate(request, request + threshold + hysteresis + 1, 'heat')
    assert power.state == False


def test_heating_power_off():
    state = False
    request = 21.0
    threshold = 1.0
    hysteresis = 0.5

    power = Power(threshold, hysteresis)

    #  above request, above threshold, above hysteresis => power off
    power.state = state
    power.calculate(request, request + threshold + hysteresis + 1, 'heat')
    assert power.state == False

    #  above request, above threshold, below hysteresis => power off
    power.state = state
    power.calculate(request, request + threshold + (hysteresis / 2), 'heat')
    assert power.state == False

    #  above request, below threshold => power on
    power.state = state
    power.calculate(request, request + (threshold / 2), 'heat')
    assert power.state == True

def test_cooling_power_on():
    state = True
    request = 21.0
    threshold = 1.0
    hysteresis = 0.5

    power = Power(threshold, hysteresis)

    #  below request, above threshold => power on
    power.state = state
    power.calculate(request, request - (threshold / 2), 'cool')
    assert power.state == True

    #  below request, below threshold, above hysteresis => power on
    power.state = state
    power.calculate(request, request - threshold - (hysteresis / 2), 'cool')
    assert power.state == True

    #  below request, below threshold, below hysteresis => power off
    power.state = state
    power.calculate(request, request - threshold - hysteresis - 1, 'cool')
    assert power.state == False

def test_cooling_power_off():
    state = False
    request = 21.0
    threshold = 1.0
    hysteresis = 0.5

    power = Power(threshold, hysteresis)

    #  below request, below threshold, below hysteresis => power off
    power.state = state
    power.calculate(request, request - threshold - hysteresis - 1, 'cool')
    assert power.state == False

    #  below request, below threshold, above hysteresis => power off
    power.state = state
    power.calculate(request, request - threshold - (hysteresis / 2), 'cool')
    assert power.state == False

    #  below request, above threshold => power on
    power.state = state
    power.calculate(request, request - (threshold / 2), 'cool')
    assert power.state == True


def test_threshold():
    power = Power(0, 0)
    params = {'a': 0.01, 'b': 0, 'c': 1}
    
    assert power._threshold(+1.0, params) == 1.0
    assert power._threshold(+0.0, params) == 1.0
    assert power._threshold(-1.0, params) == 1.01
    assert power._threshold(-10.0, params) == 2
    assert power._threshold(-20.0, params) == 5
from state import State

def test_scalingFactor():
    state = State(0, -20)

    factor = state.getScalingFactor(5)
    assert factor == 0

    factor = state.getScalingFactor(0)
    assert factor == 0

    factor = state.getScalingFactor(-10)
    assert factor == 0.5

    factor = state.getScalingFactor(-20)
    assert factor == 1

    factor = state.getScalingFactor(-25)
    assert factor == 1

def test_compensateRequestTemp():
    state = State(0, -20)
    state.setState('away')

    temp = state.compensateRequestTemp(21, 5)
    assert temp == 19

    temp = state.compensateRequestTemp(21, 0)
    assert temp == 19

    temp = state.compensateRequestTemp(21, -10)
    assert temp == 20

    temp = state.compensateRequestTemp(21, -20)
    assert temp == 21

    temp = state.compensateRequestTemp(21, -25)
    assert temp == 21

def test_compensateRequestTempDummy():
    state = State(0, -20)
    state.setState('home')

    temp = state.compensateRequestTemp(21, 5)
    assert temp == 21

    temp = state.compensateRequestTemp(21, -5)
    assert temp == 21

    temp = state.compensateRequestTemp(21, -25)
    assert temp == 21

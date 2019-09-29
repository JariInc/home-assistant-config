from fan import Fan

def test_heating():
    fan = Fan()

    # If measured temperature is over the target, the error is negative and fan should be
    #
    # error | speed
    #    -3 |     1
    #    -2 |     2
    #    -1 |     3
    #     0 |     3
    #     1 |     4
    #     2 |     5
    #     3 |     5

    # OVERHEATED
    # error < -3
    #   => speed 1
    fan.calculate(-4, 'heat')
    assert fan.speed == 1

    fan.calculate(-3, 'heat')
    assert fan.speed == 2

    fan.calculate(-2, 'heat')
    assert fan.speed == 3

    fan.calculate(-1, 'heat')
    assert fan.speed == 3

    fan.calculate(0, 'heat')
    assert fan.speed == 4

    fan.calculate(1, 'heat')
    assert fan.speed == 5

    fan.calculate(2, 'heat')
    assert fan.speed == 5

    fan.calculate(3, 'heat')
    assert fan.speed == 5

    fan.calculate(4, 'heat')
    assert fan.speed == 5

def test_cooling():
    fan = Fan()

    # If measured temperature is over the target, the error is negative and fan should be
    #
    # error | speed
    #    -3 |     5
    #    -2 |     4
    #    -1 |     3
    #     0 |     3
    #     1 |     3
    #     2 |     2
    #     3 |     1

    # OVERHEATED
    # error < -3
    #   => speed 1
    fan.calculate(-4, 'cool')
    assert fan.speed == 5

    fan.calculate(-3, 'cool')
    assert fan.speed == 4

    fan.calculate(-2, 'cool')
    assert fan.speed == 3

    fan.calculate(-1, 'cool')
    assert fan.speed == 2

    fan.calculate(0, 'cool')
    assert fan.speed == 1

    fan.calculate(1, 'cool')
    assert fan.speed == 1

    fan.calculate(2, 'cool')
    assert fan.speed == 1

    fan.calculate(3, 'cool')
    assert fan.speed == 1

    fan.calculate(4, 'cool')
    assert fan.speed == 1

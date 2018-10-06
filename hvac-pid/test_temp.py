from temp import Temp

def test_upperLimit():
    temp = Temp(1, 1, 1, 1)
    temp.setMeasurement(40)
    temp.setRequest(40)
    temp.iteratePID()

    assert temp.temp_set == 30

def test_lowerLimit():
    temp = Temp(1, 1, 1, 1)
    temp.setMeasurement(-1)
    temp.setRequest(-1)
    temp.iteratePID()

    assert temp.temp_set == 17
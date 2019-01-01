from temp import Temp

def test_upperLimit():
    temp = Temp(**{
        'Kp': 1, 
        'Ki': 1, 
        'Kd': 1,
        'temp_min': 17,
        'temp_max': 30,
    })
    temp.temp_set = 40
    temp.setMeasurement(40)
    temp.setRequest(40)
    temp.iteratePID()

    assert temp.temp_set == 30

def test_lowerLimit():
    temp = Temp(**{
        'Kp': 1, 
        'Ki': 1, 
        'Kd': 1,
        'temp_min': 17,
        'temp_max': 30,
    })
    temp.temp_set = -1
    temp.setMeasurement(-1)
    temp.setRequest(-1)
    temp.iteratePID()

    assert temp.temp_set == 17
from temp import Temp

def test_upperLimit():
    temp = Temp(**{
        'Kp': 1, 
        'Ki': 1, 
        'Kd': 1,
        'integral_max_effect': 1,
    })
    temp.setMeasurement(40)
    temp.setRequest(40)
    temp.iteratePID()

    assert temp.temp_set == 30

def test_lowerLimit():
    temp = Temp(**{
        'Kp': 1, 
        'Ki': 1, 
        'Kd': 1,
        'integral_max_effect': 1,
    })
    temp.setMeasurement(-1)
    temp.setRequest(-1)
    temp.iteratePID()

    assert temp.temp_set == 17
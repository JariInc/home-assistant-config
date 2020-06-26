from temp import Temp

def test_upperLimit():
    temp = Temp(**{
        'Kp': 1, 
        'Ki': 1, 
        'Kd': 1,
        'temp_min': 17,
        'temp_max': 30,
        'mode': 'heat',
    })
    temp.temp_set = 40
    temp.setMeasurement(40, 40)
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
        'mode': 'heat',
    })
    temp.temp_set = 17
    temp.setMeasurement(17, 17)
    temp.setRequest(17)
    temp.iteratePID()

    assert temp.temp_set == 17

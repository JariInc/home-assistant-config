from util import Util

def test_waterVapourSaturationPressure():
	expected = 36.91
	temperature = 40
	humidity = 50

	util = Util()
	P_w = util.waterVapourSaturationPressure(temperature, humidity)
	assert round(P_w, 2) == expected

def test_dewPoint():
	expected = 27.6
	temperature = 40
	humidity = 50

	util = Util()
	T_d = util.dewPoint(temperature, humidity)
	assert round(T_d, 1) == expected

def test_absoluteHumidity():
	expected = 13.82
	temperature = 20
	humidity = 80

	util = Util()
	A = util.absoluteHumidity(temperature, humidity)
	assert round(A, 2) == expected

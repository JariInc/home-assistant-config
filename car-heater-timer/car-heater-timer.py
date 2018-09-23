import logging
import os
from datetime import date, time, datetime, timedelta
from time import sleep
from hass import Hass
from dotenv import load_dotenv

load_dotenv()

class CarHeaterTimer(object):
	hass = None 
	logger = None

	def __init__(self, base_url, api_key):
		self.logger = logging.getLogger('car-heater-timer')
		self.logger.info('Starting car heater controller')

		self.hass = Hass(base_url, api_key)

	def check(self, entity):
		isArmed = self.isArmed(entity)
		isHeating = self.isHeating(entity)

		if isHeating and isArmed:
			self.logger.info('%s is heating', entity)
			
			turnOffDateTime = self.turnOffDateTime(entity)
			timeToTurnOff =  turnOffDateTime - datetime.now()

			self.logger.info('%s turn off at %s (%s minutes)', entity, turnOffDateTime.isoformat(), round(timeToTurnOff.total_seconds() / 60))

			if timeToTurnOff.total_seconds() < 0:
				self.logger.info('Turning off heating %s', entity)
				isHeating = self.setHeating(entity, False)
				self.logger.info('Disarming %s', entity)
				isHeating = self.setArming(entity, False)

		elif isArmed:
			self.logger.info('%s is armed', entity)

			departureDateTime = self.departureDateTime(entity)
			self.logger.info('%s departure at %s', entity, departureDateTime.isoformat())

			temp = self.outsideTemperature()
			heatingTime = self.heatingTime(temp)
			self.logger.info('Heating for %s minutes in %sC', heatingTime, temp)

			if heatingTime > 0:
				now = datetime.now()
				timeToDeparture = (departureDateTime - now).total_seconds()

				self.logger.info('%s minutes to departure', round(timeToDeparture / 60))

				if timeToDeparture < heatingTime * 60:
					self.logger.info('Turning on heating %s', entity)
					isHeating = self.setHeating(entity, True)


	def isArmed(self, entity):
		state = self.hass.getState('input_boolean.' + entity + '_armed')

		return state['state'] == 'on'

	def isHeating(self, entity):
		state = self.hass.getState('switch.' + entity)

		return state['state'] == 'on'

	def departureTime(self, entity):
		state = self.hass.getState('input_datetime.' + entity + '_departure')

		hour = state['attributes']['hour']
		minute = state['attributes']['minute']
		second = state['attributes']['second']
		
		return time(hour, minute, second)

	def departureDateTime(self, entity): 
		now = datetime.now()
		current_time = now.timetz()
		departure_date = now.date()
		departure_time = self.departureTime(entity)

		if(current_time > departure_time):
			departure_date += timedelta(days=1)

		departure_datetime = datetime.combine(departure_date, departure_time)

		return departure_datetime

	def turnOffDateTime(self, entity):
		departure_time = self.departureTime(entity)
		current_date = date.today()
		departure_datetime = datetime.combine(current_date, departure_time)
		turnoff_datetime = departure_datetime + timedelta(minutes=30)

		return turnoff_datetime

	def outsideTemperature(self):
		entity = os.getenv('TEMP_ENTITY')
		state = self.hass.getState(entity)

		return float(state['state'])

	def heatingTime(self, temp_C):
		temp_0m_C = 5
		temp_120m_C = -15

		temp_0m_K = temp_0m_C + 273.15
		temp_120m_K = temp_120m_C + 273.15
		temp_K = temp_C + 273.15

		delta = -120 / (temp_0m_K - temp_120m_K)
		offset = -delta * temp_0m_K
		heating_time = (delta * temp_K) + offset

		return max(min(heating_time, 180), 0)

	def setHeating(self, entity, enabled):
		if enabled:
			self.hass.callService('switch', 'turn_on', 'switch.' + entity)
		else:
			self.hass.callService('switch', 'turn_off', 'switch.' + entity)

	def setArming(self, entity, enabled):
		if enabled:
			self.hass.callService('input_boolean', 'turn_on', 'input_boolean.' + entity + '_armed')
		else:
			self.hass.callService('input_boolean', 'turn_off', 'input_boolean.' + entity + '_armed')

if __name__ == '__main__':
	logger = logging.getLogger('car-heater-timer')
	logger.setLevel(logging.DEBUG)
	logger.propagate = False

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	ch.setFormatter(formatter)

	logger.addHandler(ch)

	base_url = os.getenv('BASE_URL')
	api_key = os.getenv('API_KEY')
	entities = os.getenv('ENTITIES').split(',')

	timer = CarHeaterTimer(base_url, api_key)

	while True:
		for entity in entities:
			timer.check(entity)
		sleep(60)
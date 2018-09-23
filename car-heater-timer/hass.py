import requests
import logging

class Hass(object):
	base_url = None
	api_key = None
	base_headers = {}

	def __init__(self, base_url, api_key):
		self.base_url = base_url
		self.api_key = api_key

		self.base_headers['x-ha-access'] = api_key
		self.logger = logging.getLogger('car-heater-timer.hass')

	def getState(self, entity_id):
		r = requests.get(
			self.base_url + '/states/'+ entity_id, 
			headers=self.base_headers
		)

		return r.json()

	def callService(self, domain, service, entity_id):
		r = requests.post(
			self.base_url + '/services/'+  domain +'/'+ service, 
			headers=self.base_headers, 
			json={'entity_id': entity_id}
		)

		return r.json()
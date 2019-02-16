import requests
from bs4 import BeautifulSoup
import logging

class Scrape(object):
  baseurl = None
  cookies = {'ExtranetGDPR': 'true'}
  html = None
  fixedFormFields = {}

  def __init__(self, baseurl):
    self.baseurl = baseurl
    self.logger = logging.getLogger('oss_scrape.scrape')

  def get(self, path='/'):
    return self._request('GET', self.baseurl + path)

  def post(self, path, data):
    return self._request('POST', self.baseurl + path, data)

  def _request(self, method, url, data={}):
    data = {**data, **self.fixedFormFields}

    response = requests.request(method, url, data=data, cookies=self.cookies)

    self.logger.info("%s %s status: %s time: %s", method, response.url, response.status_code, response.elapsed)
    
    # store cookies
    self.cookies = {**self.cookies, **dict(response.cookies)}

    # store cookies from redirections
    for redirect in response.history:
      self.cookies = {**self.cookies, **dict(redirect.cookies)}

    # parse form values
    if response.headers['Content-Type'] == 'text/html; charset=iso-8859-1':
      self.html = BeautifulSoup(str(response.text), 'html.parser')
      self.fixedFormFields['__VIEWSTATE'] = self.html.select_one('#__VIEWSTATE').attrs['value']
      self.fixedFormFields['__VIEWSTATEGENERATOR'] = self.html.select_one('#__VIEWSTATEGENERATOR').attrs['value']
      self.fixedFormFields['__EVENTVALIDATION'] = self.html.select_one('#__EVENTVALIDATION').attrs['value'] if self.html.select_one('#__EVENTVALIDATION') else None
      self.fixedFormFields['__EVENTTARGET'] = self.html.select_one('#__EVENTTARGET').attrs['value'] if self.html.select_one('#__EVENTTARGET') else None
    else:
      self.html = None

    return response
import logging
from scrape import Scrape
from datetime import date, datetime
import dateutil.tz

class OSS(object):
  scrape = None
  logger = None
  baseurl = 'https://online.pset.fi'
  username = None
  password = None
  placeId = None
  initilized = False

  def __init__(self, username, password, placeId):
    self.username = username
    self.password = password
    self.placeId = placeId
    self.scrape = Scrape(self.baseurl)
    self.logger = logging.getLogger('oss_scrape.oss')

  def initilize(self):
    if not self.initilized:
      self.logger.info('Initializing OSS')
      self.login(self.username, self.password)

      today = date.today()
      
      # navigate to comsumption reporting
      self.scrape.get('/ConsumptionReporting/Default.aspx')
      self.scrape.get('/ConsumptionReporting/HourlyBasedReporting.aspx')
      self.scrape.post('/ConsumptionReporting/HourlyBasedReporting.aspx', {
        'ctl00$_ispostback': '0',
        'ctl00$ContentPlaceHolder1$ddlYearSelector': today.year,
        'ctl00$ContentPlaceHolder1$ddlReportType': 'Taulukko',
        'ctl00$ContentPlaceHolder1$ddlUnit': 'kWh',
        'ctl00$ContentPlaceHolder1$ddlCalendarDividingGroup': '' ,
        'ctl00$ContentPlaceHolder1$cblMeasurements$0': self.placeId,
        'ctl00$ContentPlaceHolder1$rblAdditionalMeasurement': 'None',
        'ctl00$langCode': '',
      })

      self.initilized = True
      self.logger.info('Initilization done')

  def login(self, username, password):
    self.scrape.get('/')
    self.scrape.post('/Login.aspx?ReturnUrl=/', {
      'ctl00$ContentPlaceHolder1$Login1$Username': username,
      'ctl00$ContentPlaceHolder1$Login1$Password': password,
      'ctl00$ContentPlaceHolder1$Login1$LoginButton': 'Kirjaudu',
    })

  def getMonthlyEnergyConsumption(self, dt):
    self.initilize()

    year = dt.year
    month = dt.month

    self.logger.info('Scraping %s/%s', month, year)

    self.scrape.post('/ConsumptionReporting/HourlyBasedReporting.aspx', {
      'ctl00$_ispostback': '0',
      'ctl00$ContentPlaceHolder1$ddlYearSelector': year,
      'ctl00$ContentPlaceHolder1$ddlMonthSelector': month,
      'ctl00$ContentPlaceHolder1$ddlResolutionSelector': 'Hour',
      'ctl00$ContentPlaceHolder1$ddlReportType': 'Taulukko',
      'ctl00$ContentPlaceHolder1$ddlUnit': 'kWh',
      'ctl00$ContentPlaceHolder1$ddlCalendarDividingGroup': '' ,
      'ctl00$ContentPlaceHolder1$cblMeasurements$0': self.placeId,
      'ctl00$ContentPlaceHolder1$rblAdditionalMeasurement': 'None',
      'ctl00$langCode': '',
    })

    table = self.scrape.html.find(id="ContentPlaceHolder1_gvMeasurements_gvMeasurements")
    data = []

    for row in table.find_all('tr'):
      cols = row.find_all('td')
      if len(cols) == 5 and cols[3].get_text().strip():
        date = datetime.strptime(cols[0].get_text(), '%d.%m.%Y %H:%M').replace(tzinfo=dateutil.tz.gettz('Europe/Helsinki'))
        energy = float(cols[3].get_text().replace(',','.'))
        data.append((date, energy))

    return data
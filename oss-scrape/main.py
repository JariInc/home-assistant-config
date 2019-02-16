import logging
import os
import sys
import pprint
from datetime import datetime
from dateutil.relativedelta import *
import dateutil.tz

from dotenv import load_dotenv

from oss import OSS
from influx import InfluxDB

load_dotenv()

if __name__ == '__main__':
  # logging
  logger = logging.getLogger('oss_scrape')
  logger.setLevel(logging.DEBUG)
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  placeId = os.getenv('OSS_PLACE_ID')

  # Scraper
  oss_options = {
    'username': os.getenv('OSS_USERNAME'),
    'password': os.getenv('OSS_PASSWORD'),
    'placeId': placeId,
  }

  oss = OSS(**oss_options)

  # InfluxDB
  db = InfluxDB(
    os.getenv('INFLUXDB_USER'),
    os.getenv('INFLUXDB_PASSWORD'),
    os.getenv('INFLUXDB_HOST')
  )

  lastDataPoint = db.getLastDataPoint('energy', 'electricity', placeId)
  currentTs = datetime.now(dateutil.tz.gettz('Europe/Helsinki'))

  logger.info('Fetching new data since %s', lastDataPoint)

  ts = lastDataPoint.astimezone(dateutil.tz.gettz('Europe/Helsinki')).replace(day=1, hour=0, minute=0)
  while ts < currentTs:
    data = oss.getMonthlyEnergyConsumption(ts)

    db.write(
      'energy', 
      'electricity', 
      {'source': 'oss', 'place_id': placeId}, 
      [i for i in data if i[0] > lastDataPoint]
    )

    ts = ts + relativedelta(months=+1)
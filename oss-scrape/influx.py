import logging
from datetime import datetime
import dateutil.parser, dateutil.tz
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

class InfluxDB(object):
  logger = None
  client = None

  def __init__(self, username, password, host, port=8086):
    self.logger = logging.getLogger('oss_scrape.influxdb')
    self.client = InfluxDBClient(host=host, port=port, username=username, password=password)

  def write(self, database, measurement, tags, data):
    dataPoints = []

    for date, energy in data:
      dataPoints.append({
        "measurement": measurement,
        "tags": tags,
        "time": date.isoformat(),
        "fields": {'consumption': energy},        
      })

    self.client.switch_database(database)

    try:
      self.logger.info('Writing %s data points to InfluxDB', len(dataPoints))
      self.client.write_points(dataPoints)
    except InfluxDBClientError as e:
      self.logger.error('InfluxDB error: %s', str(e))

  def getLastDataPoint(self, database, measurement, placeId):
    self.client.switch_database(database)
    result = self.client.query("SELECT * FROM %s WHERE source = 'oss' AND place_id = '%s' ORDER BY time DESC LIMIT 1;" % (measurement, placeId,))
    items = result.items()

    if len(items) <= 0:
      return datetime(2017, 6, 1, tzinfo=dateutil.tz.gettz('Europe/Helsinki'))
    else:
      key, generator = items[0]
      first = next(generator)
      return dateutil.parser.parse(first['time']).astimezone(dateutil.tz.gettz('Europe/Helsinki'))
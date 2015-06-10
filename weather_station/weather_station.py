import socket
import time
import logging
import uuid
import random
from db.models import WeatherStation as WeatherStationModel, MetricType as MetricTypeModel, Metric as MetricModel
from db.create_db import session
from datetime import datetime


LOG_FORMAT = ('%(levelname) -5s %(asctime)s %(name) -5s %(funcName) -5s %(lineno) -5d: %(message)s')
LOG_LEVEL = logging.DEBUG
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)


class WeatherStation(object):

    def __init__(self):
        self.interval = 5
        self.base_temperature = random.uniform(15.0, 20.0)
        self.base_humidity = random.uniform(45.0, 75.0)
        self.model = WeatherStationModel()
        self.model.name = 'ws_%s' % socket.gethostname()
        self.model.id = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.model.name))
        if not self._exists():
            self.model.deleted = 0
            self.model.is_sent = 0
            self.model.latitude = float("{0:.4f}".format(random.uniform(51.0, 54.0)))
            self.model.longitude = float("{0:.4f}".format(random.uniform(15.0, 25.0)))
            self.model.metric_types = self._available_metric_types()
            logging.debug('WS does not exists. Creating new: %s @ (%s N, %s E)' % (self.model.name,
                                                                                   self.model.latitude,
                                                                                   self.model.longitude))
            session.merge(self.model)
            session.commit()
        else:
            logging.debug('WS already exists. Doing nothing.')
            self.model = session.query(WeatherStationModel).filter_by(id=self.model.id).one()

    def _exists(self):
        weather_stations = session.query(WeatherStationModel).filter_by(id=self.model.id).all()
        return len(weather_stations) == 1

    def run(self):
        try:
            while True:
                self._generate_metrics_data()
                time.sleep(self.interval)
        except KeyboardInterrupt as keyboard_interrupt:
            logging.info('Stopped.')

    def __str__(self):
        return str(self.model.__dict__)

    def _available_metric_types(self):
        return session.query(MetricTypeModel).all()

    def _generate_metrics_data(self):
        logging.info('Added new metrics [%s]:' % len(self.model.metric_types))
        for metric_type in self.model.metric_types:
            new_metric = MetricModel()
            new_metric.metric_type = metric_type
            new_metric.metric_type_id = metric_type.id
            new_metric.id = str(uuid.uuid4())
            new_metric.is_sent = 0
            if metric_type.name == 'Temperature':
                new_metric.value = float("{0:.2f}".format(random.uniform(self.base_temperature-5,
                                                                         self.base_temperature+5)))
            elif metric_type.name == 'Humidity':
                new_metric.value = float("{0:.2f}".format(random.uniform(self.base_humidity-10,
                                                                         self.base_humidity+10)))
            else:
                new_metric.value = random.uniform(metric_type.min_value, metric_type.max_value)
            new_metric.weather_station = self.model
            new_metric.weather_station_id = self.model.id
            new_metric.timestamp = datetime.utcnow().replace(microsecond=0)
            session.add(new_metric)
            logging.debug('\t%s :\t%s %s' % (str(metric_type.name), new_metric.value, metric_type.unit))
        session.commit()

if __name__ == '__main__':
    ws = WeatherStation()
    ws.run()

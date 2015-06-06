import socket
import time
import logging
import uuid
import random
from db.models import WeatherStation as WeatherStationModel, MetricType as MetricTypeModel, Metric as MetricModel
from db.create_db import session


LOG_FORMAT = ('%(levelname) -5s %(asctime)s %(name) -10s %(funcName) -5s %(lineno) -5d: %(message)s')
LOG_LEVEL = logging.DEBUG
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)


class WeatherStation(object):

    def __init__(self):
        self.model = WeatherStationModel()
        self.model.name = 'ws_%s' % socket.gethostname()
        self.model.deleted = False
        self.model.id = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.model.name))
        self.model.is_sent = False
        self.model.latitude = random.uniform(-90.0, 90.0)
        self.model.longitude = random.uniform(-90.0, 90.0)
        self.model.metric_types = self._available_metric_types()

        self.interval = 5

        session.add(self.model)
        session.commit()

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
        for metric_type in self.model.metric_types:
            new_metric = MetricModel()
            new_metric.metric_type = metric_type
            new_metric.metric_type_id = metric_type.id
            new_metric.id = str(uuid.uuid4())
            new_metric.is_sent = False
            new_metric.value = random.uniform(metric_type.min_value, metric_type.max_value)
            new_metric.weather_station = self.model
            new_metric.weather_station_id = self.model.id
            session.add(new_metric)
        session.commit()
        logging.info('Added new metrics')

if __name__ == '__main__':
    ws = WeatherStation()
    ws.run()

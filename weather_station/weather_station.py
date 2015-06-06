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

        session.add(self.model)
        session.commit()

    def run(self):
        try:
            while True:
                logging.debug(self)
                time.sleep(5)
        except KeyboardInterrupt as keyboard_interrupt:
            logging.info('Stopped.')

    def __str__(self):
        return str(self.model.__dict__)

    def _available_metric_types(self):
        return session.query(MetricTypeModel).all()

if __name__ == '__main__':
    ws = WeatherStation()
    ws.run()

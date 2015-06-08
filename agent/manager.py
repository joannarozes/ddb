import json
import logging
import threading
import time
import pika

from db.db import session
from db.models import Metric, WeatherStation

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class AgentManager(object):
    def __init__(self, cfg):
        self._connection = None
        self._channel = None
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0
        self._stopping = False
        self._closing = False
        self.cfg = cfg
        self.EXCHANGE = self.cfg['exchange']
        self.ROUTING_KEY = self.cfg['routingKey']
        self.QUEUE = self.cfg['queue']
        self.EXCHANGE_TYPE = self.cfg['exchangeType']

    def connect(self, forever=True):
        parameters = pika.ConnectionParameters(host=str(self.cfg['broker']),
                                               port=int(self.cfg['port']),
                                               virtual_host='/')
        return pika.SelectConnection(parameters,
                             self.on_connection_open,
                             stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        LOGGER.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        LOGGER.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        # Create a new connection
        self._connection = self.connect()

        # There is now a new connection, needs a new ioloop to run
        self._connection.ioloop.start()

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        LOGGER.warning('Channel was closed: (%s) %s', reply_code, reply_text)
        if not self._closing:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        LOGGER.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        LOGGER.info('Exchange declared')
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        LOGGER.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        LOGGER.info('Binding %s to %s with %s', self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.on_bindok, self.QUEUE, self.EXCHANGE, self.ROUTING_KEY)

    def on_bindok(self, unused_frame):
        LOGGER.info('Queue bound')
        self.start_publishing()

    def start_publishing(self):
        LOGGER.info('Issuing consumer related RPC commands')
        self.enable_delivery_confirmations()
        self.fan_out()

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        LOGGER.info('Received %s for delivery tag: %i',
                    confirmation_type,
                    method_frame.method.delivery_tag)
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        LOGGER.info('Published %i messages, %i have yet to be confirmed, '
                    '%i were acked and %i were nacked',
                    self._message_number, len(self._deliveries),
                    self._acked, self._nacked)


    def close_channel(self):
        LOGGER.info('Closing the channel')
        if self._channel:
            self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        LOGGER.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()
        self._connection.ioloop.start()
        LOGGER.info('Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        LOGGER.info('Closing connection')
        self._closing = True
        self._connection.close()

    def enable_delivery_confirmations(self):
        LOGGER.info('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def _publish(self, msg):
        try:
            published = self._channel.basic_publish(self.cfg['exchange'],
                                       self.cfg['routingKey'], msg,
                                       pika.BasicProperties(
                                           content_type='application/json',
                                           delivery_mode=2),  # Persistent,
                                           mandatory=True
                                      )
            if not published:
                raise Exception('Publish unsuccessful.')
            self._message_number += 1
            self._deliveries.append(self._message_number)
            LOGGER.info('Published message # %i', self._message_number)

        except Exception as e:
            LOGGER.error('Error %s when sending message.', str(e))
            raise

    def publish_station(self, station):
        msg_dict = {
            "action": "add_station",
            "data": {
                "id": station.id,
                "name": station.name,
                "latitude": station.latitude,
                "longitude": station.longitude,
                "metric_types": [mt.id for mt in station.metric_types],
            }
        }
        msg = json.dumps(msg_dict)
        self._publish(msg)

    def publish_metric(self, metric):
        msg_dict = {
            "action": "add_metric",
            "data": {
                "id": metric.id,
                "value": metric.value,
                "metric_type_id": metric.metric_type_id,
                "weather_station_id": metric.weather_station_id,
                "timestamp": int(metric.timestamp.strftime('%s')),
            }
        }
        msg = json.dumps(msg_dict)
        self._publish(msg)

    def fan_out(self, period=30):
        LOGGER.debug('Fanning out rows...')

        stations = session.query(WeatherStation).filter_by(is_sent=0).all()
        for station in stations:
            session.begin()
            try:
                LOGGER.debug('Fanning out station %s' % str(station))
                self.publish_station(station)
                station.is_sent = 1
                session.commit()
            except Exception as e:
                LOGGER.error('Error %s when processing station.', str(e))
                session.rollback()
                raise

        metrics = session.query(Metric).filter_by(is_sent=0).all()
        for metric in metrics:
            session.begin()
            try:
                LOGGER.debug('Fanning out metric %s' % str(metric))
                self.publish_metric(metric)
                metric.is_sent = 1
                session.commit()
            except Exception as e:
                LOGGER.error('Error %s when processing metric.', str(e))
                session.rollback()
                raise

        threading.Timer(period, self.fan_out).start()  # Periodic loop.


def main():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    cfg = json.load(open("config.json"))

    manager = AgentManager(cfg)
    try:
        manager.run()
    except KeyboardInterrupt:
        manager.stop()


if __name__ == '__main__':
    main()

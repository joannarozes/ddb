import pika
import json

class Agent:

    def __init__(self):
        config = json.loads("config.json")
        credentials = pika.PlainCredentials(config.username, config.password)
        parameters = pika.ConnectionParameters(config.broker,
                                               config.port,
                                               '/',
                                               credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def publish(self, exchange, rkey, msg):
        self.channel.basic_publish(exchange,
                                   rkey,
                                   msg,
                                   pika.BasicProperties(
                                       content_type='text/plain',
                                       delivery_mode=1)
                                   )

    def __del__(self):
        self.connection.close()


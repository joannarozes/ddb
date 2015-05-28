import pika
import json

class Agent:

    def __init__(self):
        config = json.load("config.json")
        credentials = pika.PlainCredentials(config.username, config.password)
        parameters = pika.ConnectionParameters(config.broker,
                                               config.port,
                                               '/',
                                               credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def publish(self, msg):
        self.channel.basic_publish(self.config.exchange,
                                   self.config.routingKey,
                                   msg,
                                   pika.BasicProperties(
                                       content_type='text/plain',
                                       delivery_mode=1)
                                   )

    def __del__(self):
        self.connection.close()


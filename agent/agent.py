import pika
import json

class Agent(object):

    def __init__(self):
        config = json.load(open("../config.json"))
        credentials = pika.PlainCredentials(config['username'], config['password'])
        parameters = pika.ConnectionParameters(host=str(config['broker']),
                                               port=int(config['port']),
                                               virtual_host='/',
                                               credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def publish(self, msg):
        self.channel.basic_publish(self.config['exchange'],
                                   self.config['routingKey'],
                                   msg,
                                   pika.BasicProperties(
                                       content_type='text/plain',
                                       delivery_mode=1)
                                   )

    def __del__(self):
        if self.connection:
            self.connection.close()


import pika
import json

class Agent(object):

    def __init__(self):
        self.config = json.load(open("../config.json"))
        #credentials = pika.PlainCredentials(config['username'], config['password'])
        parameters = pika.ConnectionParameters(host=str(self.config['broker']),
                                               port=int(self.config['port']),
                                               virtual_host='/')
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def publish(self, msg):
        try:
            self.channel.basic_publish(self.config['exchange'],
                                   self.config['routingKey'],
                                   msg,
                                   pika.BasicProperties(
                                       content_type='text/plain',
                                       delivery_mode=1)
                                   )
        except Exception as e:
            print e

    def __del__(self):
        if self.connection:
            self.connection.close()


import pika


class Agent:

    def __init__(self):
        self.connection = pika.BlockingConnection()
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


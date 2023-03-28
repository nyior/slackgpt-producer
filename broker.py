import os,json
from typing import Callable

import pika
# from pika.exchange_type import ExchangeType
from dotenv import load_dotenv


# Load the .env file
load_dotenv()


class CloudAMQPHelper:
    """ The interface between this project and CloudAMQP """

    EXCHANGE = "slack_bot_exchange"
    EXCHANGE_TYPE = "direct"
    QUEUE_NAME = "slack_bot_queue"
    ROUTING_KEY = "slack_bot"
    
    def __create_connection(self):
        """ Sets up a connection and a channel when this class is instantiated """

        url = os.environ.get("CLOUDAMQP_URL")
        params = pika.URLParameters(url)

        connection = pika.BlockingConnection(params) # Connect to CloudAMQP
        return connection
    
    def __create_channel(
        self, connection: pika.BlockingConnection
    ) -> pika.BlockingConnection:
        channel = connection.channel() # start a channel
        return channel
        
    def __create_exchanges_queues(self, channel) -> None:
        """ Declares a queue and an exchnage using the channel created """
        # Create an exchange
        channel.exchange_declare(
            exchange=self.EXCHANGE, exchange_type=self.EXCHANGE_TYPE
        )
        # Create a queue
        channel.queue_declare(queue=self.QUEUE_NAME)
        # Bind queue with exchange
        channel.queue_bind(
            self.QUEUE_NAME,
            self.EXCHANGE, 
            self.ROUTING_KEY # The routing key here is the binding key
        )

    def publish_message(self, message_body) -> None:
        """ Publishes a message to CloudAMQP """
        connection = self.__create_connection()
        
        channel = self.__create_channel(connection=connection)
        
        # First declare an exchange and a queue
        self.__create_exchanges_queues(channel=channel)

        channel.basic_publish(
            exchange=self.EXCHANGE, 
            routing_key=self.ROUTING_KEY,
            body=json.dumps(message_body)
        )

        connection.close()


# Create an instance
cloudamqp: CloudAMQPHelper = CloudAMQPHelper()
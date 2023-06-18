import functools
import json
import os
import pika
import app.main as main

from pika.adapters.asyncio_connection import AsyncioConnection

from app.publisher.queue_settings import EXCHANGE, EXCHANGE_TYPE, QUEUE, ROUTING_KEY

# Este codigo fue extraido de los ejemplos de la documentacion de pika,
# pero se lo adapto para que funcione con el resto del codigo de la aplicacion
# de forma asincronica
# REFERENCIAS:
# - https://pika.readthedocs.io/en/stable/intro.html
# - https://pika.readthedocs.io/en/stable/examples.html
# - https://github.com/pika/pika/blob/main/examples/asynchronous_publisher_example.py
# - https://github.com/pika/pika/blob/main/examples/asyncio_consumer_example.py


class PublisherQueue:
    """This is an example publisher that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    It uses delivery confirmations and illustrates one way to keep track of
    messages that have been sent and if they've been confirmed by RabbitMQ.

    """

    instance = None  # For Singleton pattern!

    def __new__(cls, amqp_url):
        """Setup the example publisher object, passing in the URL we will use
        to connect to RabbitMQ.

        :param str amqp_url: The URL for connecting to RabbitMQ

        """
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance._connection = None
            cls.instance._channel = None

            cls.instance._deliveries = None
            cls.instance._acked = None
            cls.instance._nacked = None
            cls.instance._message_number = None

            cls.instance._stopping = False
            cls.instance._url = amqp_url

        return cls.instance

    def connect(cls):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        main.logger.info('Connecting to %s', cls.instance._url)
        return AsyncioConnection(
            pika.URLParameters(cls.instance._url),
            on_open_callback=cls.instance.on_connection_open,
            on_open_error_callback=cls.instance.on_connection_open_error,
            on_close_callback=cls.instance.on_connection_closed,
        )

    def on_connection_open(cls, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param pika.SelectConnection _unused_connection: The connection

        """
        main.logger.info('Connection opened')
        cls.instance.open_channel()

    def on_connection_open_error(cls, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        main.logger.error('Connection open failed, reopening in 5 seconds: %s', err)
        cls.instance._connection.ioloop.call_later(
            5, cls.instance._connection.ioloop.stop
        )

    def on_connection_closed(cls, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        cls.instance._channel = None
        if cls.instance._stopping:
            cls.instance._connection.ioloop.stop()
        else:
            main.logger.warning('Connection closed, reopening in 5 seconds: %s', reason)
            cls.instance._connection.ioloop.call_later(
                5, cls.instance._connection.ioloop.stop
            )

    def open_channel(cls):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.

        """
        main.logger.info('Creating a new channel')
        cls.instance._connection.channel(on_open_callback=cls.instance.on_channel_open)

    def on_channel_open(cls, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        main.logger.info('Channel opened')
        cls.instance._channel = channel
        cls.instance.add_on_channel_close_callback()
        cls.instance.setup_exchange(EXCHANGE)

    def add_on_channel_close_callback(cls):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        main.logger.info('Adding channel close callback')
        cls.instance._channel.add_on_close_callback(cls.instance.on_channel_closed)

    def on_channel_closed(cls, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed

        """
        main.logger.warning('Channel %i was closed: %s', channel, reason)
        cls.instance._channel = None
        if not cls.instance._stopping:
            cls.instance._connection.close()

    def setup_exchange(cls, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        main.logger.info('Declaring exchange %s', exchange_name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            cls.instance.on_exchange_declareok, userdata=exchange_name
        )
        cls.instance._channel.exchange_declare(
            exchange=exchange_name, exchange_type=EXCHANGE_TYPE, callback=cb
        )

    def on_exchange_declareok(cls, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)

        """
        main.logger.info('Exchange declared: %s', userdata)
        cls.instance.setup_queue(QUEUE)

    def setup_queue(cls, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        main.logger.info('Declaring queue %s', queue_name)
        cls.instance._channel.queue_declare(
            queue=queue_name, callback=cls.instance.on_queue_declareok
        )

    def on_queue_declareok(cls, _unused_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        main.logger.info('Binding %s to %s with %s', EXCHANGE, QUEUE, ROUTING_KEY)
        cls.instance._channel.queue_bind(
            QUEUE, EXCHANGE, routing_key=ROUTING_KEY, callback=cls.instance.on_bindok
        )

    def on_bindok(cls, _unused_frame):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        main.logger.info('Queue bound')
        cls.instance.start_publishing()

    def start_publishing(cls):
        """This method will enable delivery confirmations and schedule the
        first message to be sent to RabbitMQ

        """
        main.logger.info('Issuing consumer related RPC commands')
        cls.instance.enable_delivery_confirmations()

    def enable_delivery_confirmations(cls):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.

        """
        main.logger.info('Issuing Confirm.Select RPC command')
        cls.instance._channel.confirm_delivery(cls.instance.on_delivery_confirmation)

    def on_delivery_confirmation(cls, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        ack_multiple = method_frame.method.multiple
        delivery_tag = method_frame.method.delivery_tag

        main.logger.info(
            'Received %s for delivery tag: %i (multiple: %s)',
            confirmation_type,
            delivery_tag,
            ack_multiple,
        )

        if confirmation_type == 'ack':
            cls.instance._acked += 1
        elif confirmation_type == 'nack':
            cls.instance._nacked += 1

        del cls.instance._deliveries[delivery_tag]

        if ack_multiple:
            for tmp_tag in list(cls.instance._deliveries.keys()):
                if tmp_tag <= delivery_tag:
                    cls.instance._acked += 1
                    del cls.instance._deliveries[tmp_tag]
        """
        NOTE: at some point you would check cls.instance._deliveries for stale
        entries and decide to attempt re-delivery
        """

        main.logger.info(
            'Published %i messages, %i have yet to be confirmed, '
            '%i were acked and %i were nacked',
            cls.instance._message_number,
            len(cls.instance._deliveries),
            cls.instance._acked,
            cls.instance._nacked,
        )

    def publish_message(cls, message):
        if cls.instance._channel is None or not cls.instance._channel.is_open:
            return  # !TODO

        cls.instance._channel.basic_publish(
            exchange=EXCHANGE, routing_key=ROUTING_KEY, body=json.dumps(message)
        )

        cls.instance._message_number += 1
        cls.instance._deliveries[cls.instance._message_number] = True
        main.logger.info('Publishing message %s', message)

    def run(cls):
        """Run the example code by connecting and then starting the IOLoop."""
        while not cls.instance._stopping:
            cls.instance._connection = None
            cls.instance._deliveries = {}
            cls.instance._acked = 0
            cls.instance._nacked = 0
            cls.instance._message_number = 0

            try:
                cls.instance._connection = cls.instance.connect()
                cls.instance._connection.ioloop.run_forever()
            except KeyboardInterrupt:
                cls.instance.stop()
                if (
                    cls.instance._connection is not None
                    and not cls.instance._connection.is_closed
                ):
                    cls.instance._connection.ioloop.run_forever()

        main.logger.info('Stopped')

    def stop(cls):
        """Stop the example by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. The IOLoop is started because this method is
        invoked by the Try/Catch below when KeyboardInterrupt is caught.
        Starting the IOLoop again will allow the publisher to cleanly
        disconnect from RabbitMQ.

        """
        main.logger.info('Stopping')
        cls.instance._stopping = True
        cls.instance.close_channel()
        cls.instance.close_connection()

    def close_channel(cls):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.

        """
        if cls.instance._channel is not None:
            main.logger.info('Closing the channel')
            cls.instance._channel.close()

    def close_connection(cls):
        """This method closes the connection to RabbitMQ."""
        if cls.instance._connection is not None:
            main.logger.info('Closing connection')
            cls.instance._connection.close()


def getPublisherQueue() -> PublisherQueue:
    return PublisherQueue(os.environ["CLOUDAMQP_URL"])


async def runPublisherManager():
    getPublisherQueue().run()

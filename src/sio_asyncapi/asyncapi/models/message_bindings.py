from typing import Optional

from pydantic import BaseModel, Extra

from .http_bindings import HttpMessageBinding
from .web_sockets_bindings import WebSocketsMessageBinding
from .kafka_bindings import KafkaMessageBinding
from .anypoint_mq_bindings import AnypointMqMessageBinding
from .amqp_bindings import AmqpMessageBinding
from .amqp1_bindings import Amqp1MessageBinding
from .mqtt_bindings import MqttMessageBinding
from .mqtt5_bindings import Mqtt5MessageBinding
from .nats_bindings import NatsMessageBinding
from .jms_bindings import JmsMessageBinding
from .sns_bindings import SnsMessageBinding
from .solace_bindings import SolaceMessageBinding
from .sqs_bindings import SqsMessageBinding
from .stomp_bindings import StompMessageBinding
from .redis_bindings import RedisMessageBinding
from .mercure_bindings import MercureMessageBinding
from .ibm_mq_bindings import IbmMqMessageBinding

class MessageBindings(BaseModel):
    """
    Map describing protocol-specific definitions for a message.
    """

    http: Optional[HttpMessageBinding] = None
    """
    Protocol-specific information for an HTTP message, i.e., a request or a response.
    """

    ws: Optional[WebSocketsMessageBinding] = None
    """
    Protocol-specific information for a WebSockets message.
    """

    kafka: Optional[KafkaMessageBinding] = None
    """
    Protocol-specific information for a Kafka message.
    """

    anypointmq: Optional[AnypointMqMessageBinding] = None
    """
    Protocol-specific information for an Anypoint MQ message.
    """

    amqp: Optional[AmqpMessageBinding] = None
    """
    Protocol-specific information for an AMQP 0-9-1 message.
    """

    amqp1: Optional[Amqp1MessageBinding] = None
    """
    Protocol-specific information for an AMQP 1.0 message.
    """

    mqtt: Optional[MqttMessageBinding] = None
    """
    Protocol-specific information for an MQTT message.
    """

    mqtt5: Optional[Mqtt5MessageBinding] = None
    """
    Protocol-specific information for an MQTT 5 message.
    """

    nats: Optional[NatsMessageBinding] = None
    """
    Protocol-specific information for a NATS message.
    """

    jms: Optional[JmsMessageBinding] = None
    """
    Protocol-specific information for a JMS message.
    """

    sns: Optional[SnsMessageBinding] = None
    """
    Protocol-specific information for an SNS message.
    """

    solace: Optional[SolaceMessageBinding] = None
    """
    Protocol-specific information for a Solace message.
    """

    sqs: Optional[SqsMessageBinding] = None
    """
    Protocol-specific information for an SQS message.
    """

    stomp: Optional[StompMessageBinding] = None
    """
    Protocol-specific information for a STOMP message.
    """

    redis: Optional[RedisMessageBinding] = None
    """
    Protocol-specific information for a Redis message.
    """

    mercure: Optional[MercureMessageBinding] = None
    """
    Protocol-specific information for a Mercure message.
    """

    ibmmq: Optional[IbmMqMessageBinding] = None
    """
    Protocol-specific information for an IBM MQ message.
    """


    class Config:
        extra = "allow"

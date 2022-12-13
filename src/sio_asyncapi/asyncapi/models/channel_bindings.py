from typing import Optional

from pydantic import BaseModel, Extra

from .http_bindings import HttpChannelBinding
from .web_sockets_bindings import WebSocketsChannelBinding
from .kafka_bindings import KafkaChannelBinding
from .anypoint_mq_bindings import AnypointMqChannelBinding
from .amqp_bindings import AmqpChannelBinding
from .amqp1_bindings import Amqp1ChannelBinding
from .mqtt_bindings import MqttChannelBinding
from .mqtt5_bindings import Mqtt5ChannelBinding
from .nats_bindings import NatsChannelBinding
from .jms_bindings import JmsChannelBinding
from .sns_bindings import SnsChannelBinding
from .solace_bindings import SolaceChannelBinding
from .sqs_bindings import SqsChannelBinding
from .stomp_bindings import StompChannelBinding
from .redis_bindings import RedisChannelBinding
from .mercure_bindings import MercureChannelBinding
from .ibm_mq_bindings import IbmMqChannelBinding


class ChannelBindings(BaseModel):
    """
    Map describing protocol-specific definitions for a channel.
    """

    http: Optional[HttpChannelBinding] = None
    """
    Protocol-specific information for an HTTP channel.
    """

    ws: Optional[WebSocketsChannelBinding] = None
    """
    Protocol-specific information for a WebSockets channel.
    """

    kafka: Optional[KafkaChannelBinding] = None
    """
    Protocol-specific information for a Kafka channel.
    """

    anypointmq: Optional[AnypointMqChannelBinding] = None
    """
    Protocol-specific information for an Anypoint MQ channel.
    """

    amqp: Optional[AmqpChannelBinding] = None
    """
    Protocol-specific information for an AMQP 0-9-1 channel.
    """

    amqp1: Optional[Amqp1ChannelBinding] = None
    """
    Protocol-specific information for an AMQP 1.0 channel.
    """

    mqtt: Optional[MqttChannelBinding] = None
    """
    Protocol-specific information for an MQTT channel.
    """

    mqtt5: Optional[Mqtt5ChannelBinding] = None
    """
    Protocol-specific information for an MQTT 5 channel.
    """

    nats: Optional[NatsChannelBinding] = None
    """
    Protocol-specific information for a NATS channel.
    """

    jms: Optional[JmsChannelBinding] = None
    """
    Protocol-specific information for a JMS channel.
    """

    sns: Optional[SnsChannelBinding] = None
    """
    Protocol-specific information for an SNS channel.
    """

    solace: Optional[SolaceChannelBinding] = None
    """
    Protocol-specific information for a Solace channel.
    """

    sqs: Optional[SqsChannelBinding] = None
    """
    Protocol-specific information for an SQS channel.
    """

    stomp: Optional[StompChannelBinding] = None
    """
    Protocol-specific information for a STOMP channel.
    """

    redis: Optional[RedisChannelBinding] = None
    """
    Protocol-specific information for a Redis channel.
    """

    mercure: Optional[MercureChannelBinding] = None
    """
    Protocol-specific information for a Mercure channel.
    """

    ibmmq: Optional[IbmMqChannelBinding] = None
    """
    Protocol-specific information for an IBM MQ channel.
    """


    class Config:
        extra = "allow"

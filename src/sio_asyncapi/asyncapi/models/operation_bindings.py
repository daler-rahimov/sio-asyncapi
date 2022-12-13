from typing import Optional

from pydantic import BaseModel, Extra

from .http_bindings import HttpOperationBinding
from .web_sockets_bindings import WebSocketsOperationBinding
from .kafka_bindings import KafkaOperationBinding
from .anypoint_mq_bindings import AnypointMqOperationBinding
from .amqp_bindings import AmqpOperationBinding
from .amqp1_bindings import Amqp1OperationBinding
from .mqtt_bindings import MqttOperationBinding
from .mqtt5_bindings import Mqtt5OperationBinding
from .nats_bindings import NatsOperationBinding
from .jms_bindings import JmsOperationBinding
from .sns_bindings import SnsOperationBinding
from .solace_bindings import SolaceOperationBinding
from .sqs_bindings import SqsOperationBinding
from .stomp_bindings import StompOperationBinding
from .redis_bindings import RedisOperationBinding
from .mercure_bindings import MercureOperationBinding


class OperationBindings(BaseModel):
    """
    Map describing protocol-specific definitions for a operation.
    """

    http: Optional[HttpOperationBinding] = None
    """
    Protocol-specific information for an HTTP operation.
    """

    ws: Optional[WebSocketsOperationBinding] = None
    """
    Protocol-specific information for a WebSockets operation.
    """

    kafka: Optional[KafkaOperationBinding] = None
    """
    Protocol-specific information for a Kafka operation.
    """

    anypointmq: Optional[AnypointMqOperationBinding] = None
    """
    Protocol-specific information for an Anypoint MQ operation.
    """

    amqp: Optional[AmqpOperationBinding] = None
    """
    Protocol-specific information for an AMQP 0-9-1 operation.
    """

    amqp1: Optional[Amqp1OperationBinding] = None
    """
    Protocol-specific information for an AMQP 1.0 operation.
    """

    mqtt: Optional[MqttOperationBinding] = None
    """
    Protocol-specific information for an MQTT operation.
    """

    mqtt5: Optional[Mqtt5OperationBinding] = None
    """
    Protocol-specific information for an MQTT 5 operation.
    """

    nats: Optional[NatsOperationBinding] = None
    """
    Protocol-specific information for a NATS operation.
    """

    jms: Optional[JmsOperationBinding] = None
    """
    Protocol-specific information for a JMS operation.
    """

    sns: Optional[SnsOperationBinding] = None
    """
    Protocol-specific information for an SNS operation.
    """

    solace: Optional[SolaceOperationBinding] = None
    """
    Protocol-specific information for a Solace operation.
    """

    sqs: Optional[SqsOperationBinding] = None
    """
    Protocol-specific information for an SQS operation.
    """

    stomp: Optional[StompOperationBinding] = None
    """
    Protocol-specific information for a STOMP operation.
    """

    redis: Optional[RedisOperationBinding] = None
    """
    Protocol-specific information for a Redis operation.
    """

    mercure: Optional[MercureOperationBinding] = None
    """
    Protocol-specific information for a Mercure operation.
    """


    class Config:
        extra = "allow"

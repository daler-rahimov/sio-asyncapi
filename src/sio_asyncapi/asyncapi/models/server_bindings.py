from typing import Optional

from pydantic import BaseModel, Extra

from .http_bindings import HttpServerBinding
from .web_sockets_bindings import WebSocketsServerBinding
from .kafka_bindings import KafkaServerBinding
from .anypoint_mq_bindings import AnypointMqServerBinding
from .amqp_bindings import AmqpServerBinding
from .amqp1_bindings import Amqp1ServerBinding
from .mqtt_bindings import MqttServerBinding
from .mqtt5_bindings import Mqtt5ServerBinding
from .nats_bindings import NatsServerBinding
from .jms_bindings import JmsServerBinding
from .sns_bindings import SnsServerBinding
from .solace_bindings import SolaceServerBinding
from .sqs_bindings import SqsServerBinding
from .stomp_bindings import StompServerBinding
from .redis_bindings import RedisServerBinding
from .mercure_bindings import MercureServerBinding
from .ibm_mq_bindings import IbmMqServerBinding

class ServerBindings(BaseModel):
    """
    Map describing protocol-specific definitions for a server.
    """

    http: Optional[HttpServerBinding] = None
    """
    Protocol-specific information for an HTTP server.
    """

    ws: Optional[WebSocketsServerBinding] = None
    """
    Protocol-specific information for a WebSockets server.
    """

    kafka: Optional[KafkaServerBinding] = None
    """
    Protocol-specific information for a Kafka server.
    """

    anypointmq: Optional[AnypointMqServerBinding] = None
    """
    Protocol-specific information for an Anypoint MQ server.
    """

    amqp: Optional[AmqpServerBinding] = None
    """
    Protocol-specific information for an AMQP 0-9-1 server.
    """

    amqp1: Optional[Amqp1ServerBinding] = None
    """
    Protocol-specific information for an AMQP 1.0 server.
    """

    mqtt: Optional[MqttServerBinding] = None
    """
    Protocol-specific information for an MQTT server.
    """

    mqtt5: Optional[Mqtt5ServerBinding] = None
    """
    Protocol-specific information for an MQTT 5 server.
    """

    nats: Optional[NatsServerBinding] = None
    """
    Protocol-specific information for a NATS server.
    """

    jms: Optional[JmsServerBinding] = None
    """
    Protocol-specific information for a JMS server.
    """

    sns: Optional[SnsServerBinding] = None
    """
    Protocol-specific information for an SNS server.
    """

    solace: Optional[SolaceServerBinding] = None
    """
    Protocol-specific information for a Solace server.
    """

    sqs: Optional[SqsServerBinding] = None
    """
    Protocol-specific information for an SQS server.
    """

    stomp: Optional[StompServerBinding] = None
    """
    Protocol-specific information for a STOMP server.
    """

    redis: Optional[RedisServerBinding] = None
    """
    Protocol-specific information for a Redis server.
    """

    mercure: Optional[MercureServerBinding] = None
    """
    Protocol-specific information for a Mercure server.
    """

    ibmmq: Optional[IbmMqServerBinding] = None
    """
    Protocol-specific information for an IBM MQ server.
    """


    class Config:
        extra = "allow"

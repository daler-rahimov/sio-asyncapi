from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, Extra


class AmqpChannelType(str, Enum):
    queue = 'queue'
    routingKey = 'routingKey'


class AmqpExchangeType(str, Enum):
    topic = 'topic'
    direct = 'direct'
    fanout = 'fanout'
    headers = 'headers'
    default = 'default'


class AmqpExchange(BaseModel):
    """
    This object defines AMQP exchange properties.
    """

    name: Optional[str] = None
    """
    The name of the exchange. It MUST NOT exceed 255 characters long.
    """

    param_type: Optional[AmqpExchangeType] = Field(None, alias="type")
    """
    The type of the exchange. Can be either topic, direct, fanout,
    default or headers.
    """

    durable: Optional[bool] = None
    """
    Whether the exchange should survive broker restarts or not.
    """

    autoDelete: Optional[bool] = None
    """
    Whether the exchange should be deleted when the last queue is unbound from it.
    """

    vhost: Optional[str] = None
    """
    The virtual host of the exchange. Defaults to /.
    """


class AmqpQueue(BaseModel):
    """
    This object defines AMQP queue properties.
    """

    name: Optional[str] = None
    """
    The name of the queue. It MUST NOT exceed 255 characters long.
    """

    durable: Optional[bool] = None
    """
    Whether the queue should survive broker restarts or not.
    """

    exclusive: Optional[bool] = None
    """
    Whether the queue should be used only by one connection or not.
    """

    autoDelete: Optional[bool] = None
    """
    Whether the queue should be deleted when the last consumer unsubscribes.
    """

    vhost: Optional[str] = None
    """
    The virtual host of the queue. Defaults to /.
    """


class AmqpChannelBinding(BaseModel):
    """
    This object contains information about the channel representation in AMQP.
    """

    param_is: Optional[AmqpChannelType] = Field(None, alias="is")
    """
    Defines what type of channel is it. Can be either queue or routingKey (default).
    """

    exchange: Optional[AmqpExchange] = None
    """
    When is=routingKey, this object defines the exchange properties.
    """

    queue: Optional[AmqpQueue] = None
    """
    When is=queue, this object defines the queue properties.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """


class AmqpMessageBinding(BaseModel):
    """
    This object contains information about the message representation in AMQP.
    """

    contentEncoding: Optional[str] = None
    """
    A MIME encoding for the message content.
    """

    messageType: Optional[str] = None
    """
    Application-specific message type.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """


    class Config:
        extra = "allow"


class AmqpOperationBinding(BaseModel):
    """
    This document defines how to describe AMQP-specific information on AsyncAPI.
    """

    expiration: Optional[int] = None
    """
    TTL (Time-To-Live) for the message. It MUST be greater than or equal to zero.
    """

    userId: Optional[str] = None
    """
    Identifies the user who has sent the message.
    """

    cc: Optional[List[str]] = None
    """
    The routing keys the message should be routed to at the time of publishing.
    """

    priority: Optional[int] = None
    """
    A priority for the message.
    """

    deliveryMode: Optional[int] = None
    """
    Delivery mode of the message. Its value MUST be either 1 (transient) or 2
    (persistent).
    """

    mandatory: Optional[bool] = None
    """
    Whether the message is mandatory or not.
    """

    bcc: Optional[List[str]] = None
    """
    Like cc but consumers will not receive this information.
    """

    replyTo: Optional[str] = None
    """
    Name of the queue where the consumer should send the response.
    """

    timestamp: Optional[bool] = None
    """
    Whether the message should include a timestamp or not.
    """

    ack: Optional[bool] = None
    """
    Whether the consumer should ack the message or not.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                    "channels": {
                        "user/signup": {
                            "publish": {
                                "bindings": {
                                    "amqp": {
                                        "expiration": 100000,
                                        "userId": "guest",
                                        "cc": ["user.logs"],
                                        "priority": 10,
                                        "deliveryMode": 2,
                                        "mandatory": False,
                                        "bcc": ["external.audit"],
                                        "replyTo": "user.signedup",
                                        "timestamp": True,
                                        "ack": False,
                                        "bindingVersion": "0.2.0"
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        }


class AmqpServerBinding(BaseModel):
    """
    This document defines how to describe AMQP-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


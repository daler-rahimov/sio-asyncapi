from typing import Optional

from enum import Enum

from pydantic import BaseModel, Extra, Field


class IbmMqDestinationType(str, Enum):
    topic = 'topic'
    queue = 'queue'


class IbmMqTopic(BaseModel):
    """
    Defines the properties of a topic.
    """

    string: Optional[str] = None
    """
    The value of the IBM MQ topic string to be used. MUST NOT exceed 10240 characters
    in length. MAY coexist with topic.objectName
    """

    objectName: Optional[str] = None
    """
    The name of the IBM MQ topic object. MUST NOT exceed 48 characters in length. MAY
    coexist with topic.string
    """

    durablePermitted: Optional[bool] = None
    """
    Defines if the subscription may be durable.
    """

    lastMsgRetained: Optional[bool] = None
    """
    Defines if the last message published will be made available to new subscriptions.
    """


    class Config:
        extra = "allow"


class IbmMqQueue(BaseModel):
    """
    Defines the properties of a queue.
    """

    objectName: str = ...
    """
    Defines the name of the IBM MQ queue associated with the channel.
    A value MUST be specified. MUST NOT exceed 48 characters in length.
    MUST be a valid IBM MQ queue name
    """

    isPartitioned: Optional[bool] = None
    """
    Defines if the queue is a cluster queue and therefore partitioned.
    If true, a binding option MAY be specified when accessing the queue.
    More information on binding options can be found on this page in the
    IBM MQ Knowledge Center.

    If false, binding options SHOULD NOT be specified when accessing the queue.
    """

    exclusive: Optional[bool] = None
    """
    Specifies if it is recommended to open the queue exclusively.
    """


    class Config:
        extra = "allow"


class IbmMqChannelBinding(BaseModel):
    """
    This object contains information about the channel representation in IBM MQ.
    Each channel corresponds to a Queue or Topic within IBM MQ.
    """

    destinationType: Optional[IbmMqDestinationType] = None
    """
    Defines the type of AsyncAPI channel.
    """

    queue: Optional[IbmMqQueue] = None
    """
    Defines the properties of a queue.
    """

    topic: Optional[IbmMqTopic] = None
    """
    Defines the properties of a topic.
    queue and topic fields MUST NOT coexist within a channel binding.
    """

    maxMsgLength: Optional[int] = None
    """
    The maximum length of the physical message (in bytes) accepted by the Topic or Queue.
    Messages produced that are greater in size than this value may fail to be delivered.
    More information on the maximum message length can be found on this page in the IBM
    MQ Knowledge Center.

    MUST be 0-104,857,600 bytes (100 MB).
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding.
    """


    class Config:
        extra = "allow"


class IbmMqMessageBinding(BaseModel):
    """
    This object contains information about the message representation in IBM MQ.
    """

    param_type: Optional[str] = Field(None, alias="type")
    """
    The type of the message. MUST be either string, jms or binary.
    """

    headers: Optional[str] = None
    """
    Defines the IBM MQ message headers to include with this message. More than one
    header can be specified as a comma separated list. Supporting information on IBM
    MQ message formats can be found on this page in the IBM MQ Knowledge Center.

    headers MUST NOT be specified if type = string or jms
    """

    description: Optional[str] = None
    """
    Provides additional information for application developers: describes the message
    type or format.
    """

    expiry: Optional[int] = None
    """
    The recommended setting the client should use for the TTL (Time-To-Live) of the
    message. This is a period of time expressed in milliseconds and set by the
    application that puts the message. expiry values are API dependant e.g., MQI and
    JMS use different units of time and default values for unlimited. General
    information on IBM MQ message expiry can be found on this page in the IBM MQ
    Knowledge Center.

    expiry value MUST be either zero (unlimited) or greater than zero.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding.
    """


    class Config:
        extra = "allow"



class IbmMqServerBinding(BaseModel):
    """
    This document defines how to describe IBM MQ specific information with AsyncAPI.
    """

    groupId: Optional[str] = None
    """
    Defines a logical group of IBM MQ server objects. This is necessary to specify
    multi-endpoint configurations used in high availability deployments. If omitted,
    the server object is not part of a group.
    """

    ccdtQueueManagerName: Optional[str] = None
    """
    The name of the IBM MQ queue manager to bind to in the CCDT file.
    """

    cipherSpec: Optional[str] = None
    """
    The recommended cipher specification used to establish a TLS connection between
    the client and the IBM MQ queue manager.
    """

    multiEndpointServer: Optional[bool] = None
    """
    If multiEndpointServer is true then multiple connections can be workload balanced
    and applications should not make assumptions as to where messages are processed.
    Where message ordering, or affinity to specific message resources is necessary, a
    single endpoint (multiEndpointServer = false) may be required.
    """

    heartBeatInterval: Optional[int] = None
    """
    The recommended value (in seconds) for the heartbeat sent to the queue manager
    during periods of inactivity. A value of zero means that no heart beats are sent.
    A value of 1 means that the client will use the value defined by the queue manager.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding.
    """

    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                    "servers": {
                        "production1": {
                            "url": "ibmmq://qmgr1host:1414/qm1/DEV.APP.SVRCONN",
                            "protocol": "ibmmq-secure",
                            "description": "Production Instance 1",
                            "bindings": {
                                "ibmmq": {
                                    "groupId": "PRODCLSTR1",
                                    "cipherSpec": "ANY_TLS12_OR_HIGHER",
                                    "bindingVersion": "0.1.0"
                                }
                            }
                        }
                    }
                }
            ]
        }

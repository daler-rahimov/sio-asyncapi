from typing import Optional

from pydantic import BaseModel, Extra


class MqttChannelBinding(BaseModel):
    """
    This document defines how to describe MQTT-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class MqttMessageBinding(BaseModel):
    """
    This object contains information about the message representation in MQTT.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """


    class Config:
        extra = "allow"


class MqttOperationBinding(BaseModel):
    """
    This object contains information about the operation representation in MQTT.
    """

    qos: Optional[int] = None
    """
    Defines the Quality of Service (QoS) levels for the message flow between client
    and server. Its value MUST be either 0 (At most once delivery), 1 (At least
    once delivery), or 2 (Exactly once delivery).
    """

    retain: Optional[bool] = None
    """
    Whether the broker should retain the message or not.
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
                                    "mqtt": {
                                        "qos": 2,
                                        "retain": True,
                                        "bindingVersion": "0.1.0"
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        }


class MqttLastWill(BaseModel):
    """
    Last Will and Testament configuration.
    """

    topic: Optional[str] = None
    """
    The topic where the Last Will and Testament message will be sent.
    """

    qos: Optional[int] = None
    """
    Defines how hard the broker/client will try to ensure that the Last Will
    and Testament message is received. Its value MUST be either 0, 1 or 2.
    """

    message: Optional[str] = None
    """
    Last Will message.
    """

    retain: Optional[bool] = None
    """
    Whether the broker should retain the Last Will and Testament message or not.
    """

    class Config:
        extra = "allow"


class MqttServerBinding(BaseModel):
    """
    This document defines how to describe MQTT-specific information on AsyncAPI.
    """

    clientId: Optional[str] = None
    """
    The client identifier.
    """

    cleanSession: Optional[bool] = None
    """
    Whether to create a persisten connection or not. When false, the connection
    will be persistent.
    """

    lastWill: Optional[MqttLastWill] = None
    """
    Last Will and Testament configuration.
    """

    keepAlive: Optional[int] = None
    """
    Interval in seconds of the longest period of time the broker and the client
    can endure without sending a message.
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
                    "servers": {
                        "production": {
                            "bindings": {
                                "mqtt": {
                                    "clientId": "guest",
                                    "cleanSession": True,
                                    "lastWill": {
                                        "topic": "/last-wills",
                                        "qos": 2,
                                        "message": "Guest gone offline.",
                                        "retain": False
                                    },
                                    "keepAlive": 60,
                                    "bindingVersion": "0.1.0"
                                }
                            }
                        }
                    }
                }
            ]
        }

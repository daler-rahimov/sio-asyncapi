from typing import Optional, Dict, Union

from pydantic import BaseModel, Extra, Field

from .reference import Reference
from .schema import Schema


class MessageExample(BaseModel):
    """
    Message Example Object represents an example of a Message Object and MUST
    contain either headers and/or payload fields.
    """

    headers: Optional[Dict[str, Union[Schema, Reference]]] = None
    """
    The value of this field MUST validate against the Message Object's headers field.
    """

    payload: Optional[Schema] = None
    """
    The value of this field MUST validate against the Message Object's payload field.
    """

    name: Optional[str] = None
    """
    A machine-friendly name.
    """

    summary: Optional[str] = None
    """
    A short summary of what the example is about.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                    "name": "SimpleSignup",
                    "summary": "A simple UserSignup example message",
                    "headers": {
                        "correlationId": "my-correlation-id",
                        "applicationInstanceId": "myInstanceId"
                    },
                    "payload": {
                        "user": {
                            "someUserKey": "someUserValue"
                        },
                        "signup": {
                            "someSignupKey": "someSignupValue"
                        }
                    }
                }
            ]
        }


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

from functools import partial, wraps
import inspect
from typing import Callable, Optional, Type

from . import asycnapi_spec as spec
from flask import Flask, Request
from flask_socketio import SocketIO
from pydantic import BaseModel, ValidationError

from loguru import logger


class RequestValidationError(Exception):
    pass

class ResponseValidationError(Exception):
    pass

class AsyncAPISocketIO(SocketIO):
    """Inherits the :class:`flask_socketio.SocketIO` class.
    Adds ability to validate with pydantic models.

    Example::
        socket = AsyncAPISocketIO(app, async_mode='threading', logger=True)
        class TokenModel(BaseModel):
            token: int

        class RequestTokenModel(BaseModel):
            type: "str"

        @socket.on('get_token', response_model=TokenModel, request_model=RequestTokenModel)
        def get_token(message):
            return {"token": 1234}
    """

    def __init__(
        self,
        app: Optional[Flask]=None,
        validation: bool = True,
        generate_doc:bool = False,
        doc_template: Optional[str] = None,
        **kwargs,
    ):
        """Create AsycnAPISocketIO

        Args:
            app (Optional[Flask]): flask app
            validation (bool, optional): If True request and response will be validated. Defaults to True.
            generate_doc (bool, optional): If True AsyncAPI specs will be generated. Defaults to False.
            doc_template (Optional[str], optional): AsyncAPI YMAL template. Defaults to None.
        """
        self.validation = validation
        self.generate_doc = generate_doc
        if self.generate_doc:
           spec.load_spec_template(doc_template)
        super().__init__(app=app, **kwargs)


    def on_error_default(self, *args, **kwargs):
        """Decorator to register a SocketIO error handler with additional
        functionalities.  If no arguments default Flask-SocketIO error handler
        if `model` is provided it's used for generating AsyncAPI spec and validation.

        Example::

            @socketio.on_error_default(model=SocketError)
            def default_error_handler(e):
                pass
        Args:
            model (Optional[BaseModel], optional): pydantic model. Defaults to None.

        """
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # the decorator was invoked without arguments
            # args[0] is the decorated function
            return super().on_error_default(args[0])
        else:
            # the decorator was invoked with arguments
            assert kwargs.get("model") is not None, "model is required"
            # TODO: add to spec and validation here
            _super = super()
            def set_on_error_default(exception_handler):
                return _super.on_error_default(exception_handler)

            return set_on_error_default

    def on(
            self,
            message,
            namespace=None,
            *,
            get_from_typehint: bool = False,
            response_model: Optional[Type[BaseModel]] = None,
            request_model: Optional[Type[BaseModel]] = None
    ):
        """Decorator to register a SocketIO event handler with additional functionalities

        Args:
            message (str): refer to SocketIO.on(message)
            namespace (str, optional): refer to SocketIO.on(namespace). Defaults to None.
            return_value (Optional[str], optional): Return single value instead of entire
                object. Defaults to None.
            get_from_typehint (bool, optional): Get request and response models from typehint.
                request_model and response_model take precedence over typehints if not None.
                Defaults to False.
            response_model (Optional[Type[BaseModel]], optional): Acknowledge model used
                for validation and documentation. Defaults to None.
            request_model (Optional[Type[BaseModel]], optional): Request payload model used
                for validation and documentation. Defaults to None.
        """
        def decorator(handler: Callable):

            nonlocal request_model
            nonlocal response_model
            if get_from_typehint:
                first_arg_name = inspect.getfullargspec(handler)[0][0]
                posible_request_model = handler.__annotations__.get(first_arg_name)
                posible_response_model = handler.__annotations__.get("return")
                if request_model is None:
                    request_model = posible_request_model
                if response_model is None:
                    response_model = posible_response_model

            # print(f"request_model: {request_model}")
            # print(f"response_model: {response_model}")

            if self.generate_doc:
                spec.add_new_receiver(
                    handler,
                    message,
                    ack_data_model=response_model,
                    payload_model=request_model,
                    use_std_serialize=False
                )

            def wrapper(*args, **kwargs):
                # return handler(*args, **kwargs)
                new_handler = self._handle_all(
                    request_model=request_model,
                    response_model=response_model
                )(handler)
                return new_handler(*args, **kwargs)

            # Decorate with SocketIO.on decorator
            super(AsyncAPISocketIO, self).on(message, namespace)(wrapper)
            return wrapper
        return decorator

    def _handle_all(self,
                    response_model: Optional[Type[BaseModel]] = None,
                    request_model: Optional[Type[BaseModel]] = None
                    ):
        """Decorator to validate request and response with pydantic models
        Args:
            handler (Callable, optional): handler function. Defaults to None.
            response_model (Optional[Type[BaseModel]], optional): Acknowledge model used
                for validation and documentation. Defaults to None.
            request_model (Optional[Type[BaseModel]], optional): Request payload model used
                for validation and documentation. Defaults to None.

        Raises: RequestValidationError, ResponseValidationError
        """

        def decorator(handler: Callable):

            def wrapper(*args, **kwargs):
                request = args[0] if len(args) > 0 else None
                if not request:
                    request = kwargs.get("request")
                if request:
                    try:
                        if self.validation and request_model:
                            request_model.validate(request)# this will raise ValidationError
                    except ValidationError as e:
                        logger.error(f"ValidationError for incoming request: {e}")
                        raise RequestValidationError(e)

                    response = handler(*args, **kwargs)
                    try:
                        if self.validation and response_model:
                            response_model.validate(response)
                    except ValidationError as e:
                        logger.error(f"ValidationError for outgoing response: {e}")
                        raise ResponseValidationError(e)

                    if isinstance(response, BaseModel):
                        return response.json()
                    else:
                        return response
                else:
                    return handler(*args, **kwargs)

            return wrapper
        return decorator


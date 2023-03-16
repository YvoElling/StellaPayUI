from typing import Any, Union

from utils.async_requests.AsyncData import AsyncData
from utils.async_requests.AsyncError import AsyncError


class AsyncResult:
    """
    An object of this class represents a result that is received after some time. The result will indicate whether a
    result was successfully obtained or not using the ``received_result`` member variable. If this variable is False,
    you can expect ``result`` to be of type `AsyncError`. Otherwise, it will be of type `AsyncData`.
    """

    def __init__(self, success: bool, data: Any = None, error_message: str = ""):
        self.received_result = success
        self.result: Union[AsyncData, AsyncError, None] = AsyncData(data) if success else AsyncError(error_message)

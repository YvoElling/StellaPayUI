from enum import Enum

hostname = "http://staartvin.com:8181/"


class BackendURLs(Enum):
    AUTHENTICATE = hostname + "authenticate"

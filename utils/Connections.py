from enum import Enum

hostname = "http://staartvin.com:8181/"


class BackendURLs(Enum):
    AUTHENTICATE = hostname + "authenticate"
    GET_CATEGORIES = hostname + "categories"
    GET_PRODUCTS = hostname + "products/"
    CREATE_TRANSACTION = hostname + "transactions/create"
    REQUEST_USER_INFO = hostname + "identification/request-user/"
    GET_USERS = hostname + "users"
    ADD_USER_MAPPING = hostname + "identification/add-card-mapping"

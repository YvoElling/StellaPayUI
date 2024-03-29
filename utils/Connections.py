hostname = "http://159.69.87.82:8181/"


def get_hostname():
    return hostname


def authenticate() -> str:
    return get_hostname() + "authenticate"


def get_categories() -> str:
    return get_hostname() + "categories"


def get_products() -> str:
    return get_hostname() + "products/"


def create_transaction() -> str:
    return get_hostname() + "transactions/create"


def get_all_transactions() -> str:
    return get_hostname() + "transactions/all"


def request_user_info() -> str:
    return get_hostname() + "identification/request-user/"


def get_users() -> str:
    return get_hostname() + "users"


def add_user_mapping() -> str:
    return get_hostname() + "identification/add-card-mapping"


def connection_status() -> str:
    return get_hostname() + "admin"


def get_all_cards() -> str:
    return get_hostname() + "identification/cards"

# class BackendURLs:
#     AUTHENTICATE = hostname + "authenticate"
#     GET_CATEGORIES = hostname + "categories"
#     GET_PRODUCTS = hostname + "products/"
#     CREATE_TRANSACTION = hostname + "transactions/create"
#     REQUEST_USER_INFO = hostname + "identification/request-user/"
#     GET_USERS = hostname + "users"
#     ADD_USER_MAPPING = hostname + "identification/add-card-mapping"

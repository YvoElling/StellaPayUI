from enum import Enum
from typing import Any


class ConfigurationOption(Enum):

    # Seconds to wait before we start authentication to the backend
    TIME_TO_WAIT_BEFORE_AUTHENTICATING = "runtime", "time_to_wait_before_authenticating", 5

    # Seconds to wait until we try to update the offline storage again
    TIME_BETWEEN_UPDATING_OFFLINE_STORAGE = "runtime", "time_between_offline_storage_updates", 5*60

    # How many seconds do we wait until we check our connection status?
    TIME_BETWEEN_CHECKING_INTERNET_STATUS = "runtime", "time_between_checking_internet_status", 10

    # Hostname to the backend
    HOSTNAME_OF_BACKEND = "server", "hostname", "http://159.69.87.82:8181/"

    DEVICE_WIDTH = "device", "width", 1280
    DEVICE_HEIGHT = "device", "height", 720
    DEVICE_SHOW_FULLSCREEN = "device", "fullscreen", False
    DEVICE_SHOW_CURSOR = "device", "show_cursor", False

    def __init__(self, section_name: str, config_name: str, default_value: Any):
        self.section_name = section_name
        self.config_name = config_name
        self.default_value = default_value




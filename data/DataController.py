from typing import Callable, Optional, Dict

from data.OnlineDataStorage import OnlineDataStorage


class DataController:
    """
    This class is responsible for loading and storing data that the application needs. This might be user data or
    product data.

    This class should be used to retrieve data as it hides where it gets the data from (either offline or online
    storage). The DataController is responsible for deciding where the info comes from.

    """

    def __init__(self):
        self.online_data_storage = OnlineDataStorage()

    def get_user_data(self, callback: Callable[[Optional[Dict[str, str]]], None] = None) -> None:
        """
        Get a mapping of all users and their e-mail addresses. Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The user data is returned as a dictionary, where the key (str) is the username and the corresponding value (str)
        is the associated e-mail address.

        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents a dictionary of users. This might also be None!

        :return: Nothing.
        """

        # Pass the callback to the appropriate method.
        # TODO: Determine whether we should use the online or offline storage
        self.online_data_storage.get_user_data(callback=callback)


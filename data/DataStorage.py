from abc import abstractmethod
from typing import List, Callable, Optional, Dict

from ds.NFCCardInfo import NFCCardInfo
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart


class DataStorage:

    @abstractmethod
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

    @abstractmethod
    def get_product_data(self, callback: Callable[[Optional[List[Product]]], None] = None) -> None:
        """
        Get a list of all products. Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The product data is returned as a list, where each element corresponds to a Product object.

        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents a list of products. This might also be None!

        :return: Nothing.
        """
        raise NotImplementedError

    @abstractmethod
    def get_category_data(self, callback: Callable[[Optional[List[str]]], None] = None) -> None:
        """
        Get a list of all categories. Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The category data is returned as a list, where each element is the name of category (as a string).

        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents a list of categories. This might also be None!

        :return: Nothing.
        """
        raise NotImplementedError

    @abstractmethod
    def get_card_info(self, card_id=None, callback: Callable[[Optional[NFCCardInfo]], None] = None) -> None:
        """
        Get info of a particular card. Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The card info will be returned as a NFCCardInfo object.

        :param card_id: id of the card
        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents the card info. This might also be None!
        :return: Nothing.
        """
        raise NotImplementedError

    def register_card_info(self, card_id: str = None, email: str = None, callback: [[bool], None] = None) -> None:
        """
        Register a new card for a particular user.
        :param card_id: Id of the card that you want to register
        :param email: E-mail address of the user that you want to match this card with.
        :param callback: Method called when this method is finished. The callback will have one argument (boolean)
            that indicates whether the card has been registered (true) or not (false).
        :return: Nothing
        """
        raise NotImplementedError

    def create_transactions(self, shopping_cart: ShoppingCart = None, callback: Callable[[bool], None] = None) -> None:
        """
        Create a transaction (or multiple) of goods. Note that you'll need to provide a callback function
        that will be called whenever the call is completed.

        :param shopping_cart: Shopping cart that has all transactions you want to create
        :param callback: Method called when this method is finished. The callback will have one argument (boolean)
            that indicates whether the transactions have been registered (true) or not (false).
        :return: Nothing
        """
        raise NotImplementedError

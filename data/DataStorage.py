from abc import abstractmethod
from typing import List, Optional, Dict

from data.user.user_data import UserData
from ds.NFCCardInfo import NFCCardInfo
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart


class DataStorage:
    @abstractmethod
    async def get_user_data(self) -> List[UserData]:
        """
        Get a mapping of all users and their e-mail addresses. Note that this method is asynchronous and thus needs to
        be awaited.

        :return: a list of ``UserData`` objects.
        """

    @abstractmethod
    async def get_product_data(self) -> Dict[str, List[Product]]:
        """
        Get a list of all products in their corresponding categories. Note that this is an asynchronous method and needs
        to be awaited!

        :return: a dictionary is returned where the key is a category name and the value a list of products in that category
        """
        raise NotImplementedError

    @abstractmethod
    async def get_category_data(self) -> List[str]:
        """
        Get a list of all categories. Note that this is an asynchronous method and needs to be awaited!

        :return: a list of categories
        """
        raise NotImplementedError

    @abstractmethod
    async def get_card_info(self, card_id) -> Optional[NFCCardInfo]:
        """
        Get info of a particular card. Note that this method is asynchronous and thus needs to be awaited.

        The card info will be returned as a `NFCCardInfo` object.

        :param card_id: Id of the card to look for
        :return: a `NFCCardInfo` object if matching the given ``card_id`` or None if nothing could be found
        """
        raise NotImplementedError

    async def register_card_info(self, card_id: str = None, email: str = None, owner: str = None) -> bool:
        """
        Register a new card for a particular user.

        :param card_id: Id of the card that you want to register
        :param email: E-mail address of the user that you want to match this card with.
        :param owner: Name of the owner of the card
        :return: Whether the card has been registered (true) or not (false).
        """
        raise NotImplementedError

    async def create_transactions(self, shopping_cart: ShoppingCart = None) -> bool:
        """
        Create a transaction (or multiple) of goods.

        :param shopping_cart: Shopping cart that has all transactions you want to create
        :return: Whether the transactions have been registered (true) or not (false).
        """
        raise NotImplementedError

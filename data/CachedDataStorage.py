from collections import OrderedDict, defaultdict
from typing import List, Dict, Optional

from ds.NFCCardInfo import NFCCardInfo
from ds.Product import Product


class CachedDataStorage:
    """
    The goal of this class is store cached data that is retrieved either from online or offline storage. This allows
    the two types of data systems to cache data at the same time and also retrieve data from each other.
    """

    def __init__(self):
        # Cached users. Key is name, value is emailaddress
        self.cached_user_data: OrderedDict[str, str] = OrderedDict()

        # Cached product data. Key is category name, value is list of products in that category.
        self.cached_product_data: Dict[str, List[Product]] = defaultdict(list)

        # Cached categories. List of category names
        self.cached_category_data: List[str] = []

        # Cached card info. Key is card_id and value is NFCCardInfo object
        self.cached_card_info: Dict[str, NFCCardInfo] = {}

    def get_cached_user_data(self, user_name: str) -> Optional[str]:
        if user_name not in self.cached_user_data:
            return None

        return self.cached_user_data[user_name]

    def get_cached_products_of_category(self, category_name: str) -> Optional[List[Product]]:
        if category_name not in self.cached_product_data:
            return None

        return self.cached_product_data[category_name]

    def get_cached_product_data(self, product_name: str, category_name: Optional[str] = None) -> Optional[Product]:
        # Look through a specific category of products
        if category_name is not None:
            for product in self.get_cached_products_of_category(category_name):
                if product.get_name() == product_name:
                    return product
        else:
            # Loop through all categories instead
            for category, products in self.cached_product_data.items():
                for product in products:
                    if product.get_name() == product_name:
                        return product

        return None

    def get_cached_card_info(self, card_id: str) -> Optional[NFCCardInfo]:
        if card_id not in self.cached_card_info:
            return None

        return self.cached_card_info[card_id]

class Product:

    #
    # Creates a product object
    #
    def __init__(self, name, price, shown):
        self.__product_name = name
        self.__price = price
        self.__shown = shown

    #
    # create Product object directly from json file
    #
    def create_from_json(self, json):
        self.__product_name = json['name']
        self.__price = json['price']
        self.__shown = json['shown']
        return self

    #
    # Empty constructor for when the objects
    # member variables are filled directly from
    # the JSON file
    #
    def __init__(self):
        pass

    #
    # return the name of this product object
    #
    def get_name(self):
        return self.__product_name

    #
    # return the price of this object
    #
    def get_price(self):
        return self.__price
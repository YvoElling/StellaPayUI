class NFCCardInfo:
    """
    Class to store info for a particular NFC card.
    """

    def __init__(self, card_id: str, owner_name: str, owner_email: str):
        self.card_id = card_id
        self.owner_name = owner_name
        self.owner_email = owner_email

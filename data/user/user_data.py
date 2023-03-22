from dataclasses import dataclass


@dataclass(frozen=True)
class UserData:
    """
    A immutable data object representing a user and its data
    """

    real_name: str = ""
    email_address: str = ""

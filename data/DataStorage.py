from abc import abstractmethod
from typing import List, Collection, Callable, Optional, Any, Dict


class DataStorage:

    @abstractmethod
    def get_user_data(self, callback: Callable[[Optional[Dict[str, str]]], None] = None) -> None: raise NotImplementedError
    """
    Grab the data of all users. Since this method may take some time, you need to attach a callback to retrieve the 
    data once it's loaded.
    """




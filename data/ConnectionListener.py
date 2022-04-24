from abc import abstractmethod, ABC


class ConnectionListener(ABC):

    @abstractmethod
    def on_connection_change(self, connection_status: bool):
        """
        This method is called whenever the connection to the backend has been established (or lost).
        Note that this method will only be called once on a change. It will only call this method again when a connection
        has been established or lost
        :param connection_status: true when the backend could be reached again, false if the connection was lost
        :return: nothing
        """
        pass

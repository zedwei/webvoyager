from enum import Enum
from abc import ABC, abstractmethod


class ClientMode(Enum):
    LOCAL = 1
    SERVER = 2


class Client(ABC):
    @abstractmethod
    async def init(self):
        pass

    @abstractmethod
    async def user_input(self):
        pass

    @abstractmethod
    async def navigate(self):
        pass

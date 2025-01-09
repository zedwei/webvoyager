from enum import Enum
from abc import ABC, abstractmethod


class ClientMode(Enum):
    LOCAL = 1
    WEBSOCKET = 2


class Client(ABC):
    @abstractmethod
    async def run(self):
        pass

    @abstractmethod
    async def user_query(self):
        pass

    @abstractmethod
    async def navigate(self):
        pass

    @abstractmethod
    async def click(self, x, y):
        pass

    @abstractmethod
    async def run_js(self, script):
        pass

    @abstractmethod
    async def type(self, x, y, text):
        pass

    @abstractmethod
    async def scroll(self, offset):
        pass

    @abstractmethod
    async def go_back(self):
        pass

    @abstractmethod
    async def navigate(self, url):
        pass

    @abstractmethod
    async def search(self):
        pass

    @abstractmethod
    async def user_clarify(self, question):
        pass

    @abstractmethod
    async def screenshot(self):
        pass

    @abstractmethod
    async def url(self):
        pass
    
    @abstractmethod
    async def keypress(self, key):
        pass
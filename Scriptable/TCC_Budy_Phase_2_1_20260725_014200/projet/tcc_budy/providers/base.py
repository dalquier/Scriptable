from abc import ABC, abstractmethod


class ResponseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def respond(self, messages) -> str:
        raise NotImplementedError

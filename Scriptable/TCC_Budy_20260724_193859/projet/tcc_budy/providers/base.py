from abc import ABC, abstractmethod


class ResponseProvider(ABC):
    @abstractmethod
    def respond(self, text: str) -> str:
        raise NotImplementedError

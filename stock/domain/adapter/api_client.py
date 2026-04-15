from abc import ABC, abstractmethod


class IApiClient(ABC):
    @abstractmethod
    def get_account_info(self):
        raise NotImplementedError

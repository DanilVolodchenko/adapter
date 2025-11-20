import abc
from collections.abc import Callable


class IMovingObj(abc.ABC):

    @property
    @abc.abstractmethod
    def location(self):
        ...

    @location.setter
    @abc.abstractmethod
    def location(self, value):
        ...


class ICommand(abc.ABC):

    @abc.abstractmethod
    def execute(self) -> None:
        """Выполнение действия."""


class IResolver(abc.ABC):

    @abc.abstractmethod
    def resolve(self, dependency: str, *args) -> Callable:
        """Разрешает какие-либо зависимости."""


class IAdapterFactory(abc.ABC):

    @abc.abstractmethod
    def create(self, obj):
        """Возвращает адаптер."""

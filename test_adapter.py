import abc
from typing import Any
from unittest.mock import Mock

from interfaces import ICommand
from ioc import IoC, InitCommand


class IMovingObjMock(abc.ABC):

    @property
    @abc.abstractmethod
    def location(self):
        ...

    @location.setter
    @abc.abstractmethod
    def location(self, value):
        ...

    @property
    @abc.abstractmethod
    def velocity(self):
        ...

    @abc.abstractmethod
    def return_string(self) -> str:
        ...


class MockGameItem:
    properties = {}

    def add_property(self, name: str, value: Any) -> None:
        self.properties[name] = value

    def get_value(self, property_name: str) -> Any:
        return self.properties[property_name]

    def set_value(self, property_name: str, value: Any) -> None:
        self.properties[property_name] = value

    def return_string(self) -> str:
        return 'string'


def test_generated_adapter_name() -> None:
    """Получение адаптера из объекта IoC с генерированным названием."""

    InitCommand().execute()
    mock_obj = Mock()
    adapter_obj = IoC.resolve('Adapter', IMovingObjMock, mock_obj)

    assert adapter_obj.__class__.__name__ == 'MovingObjMockAdapter'


def test_get_generated_properties_game_item() -> None:
    """Получение сгенерированных свойств объекта."""

    InitCommand().execute()
    IoC[ICommand].resolve(
        'IoC.Dependency.Register', 'MockGameItem', lambda *args: MockGameItem()
    ).execute()
    IoC[ICommand].resolve(
        'IoC.Dependency.Register', 'IMovingObjMock.location.Get', lambda obj: obj.get_value('location')
    ).execute()
    IoC[ICommand].resolve(
        'IoC.Dependency.Register', 'IMovingObjMock.velocity.Get', lambda obj: obj.get_value('velocity')
    ).execute()
    mock_obj: MockGameItem = IoC.resolve('MockGameItem')
    mock_obj.add_property('location', 12345)
    mock_obj.add_property('velocity', 98765)
    adapter_obj = IoC.resolve('Adapter', IMovingObjMock, mock_obj)

    assert adapter_obj.location == 12345
    assert adapter_obj.velocity == 98765


def test_set_generated_properties_game_item() -> None:
    """Обновление сгенерированных свойств объекта."""

    class SetLocationCommand(ICommand):
        def __init__(self, obj, property_name, value):
            self.obj = obj
            self.property_name = property_name
            self.value = value

        def execute(self) -> None:
            self.obj.set_value(self.property_name, self.value)

    InitCommand().execute()
    IoC[ICommand].resolve(
        'IoC.Dependency.Register', 'MockGameItem', lambda *args: MockGameItem()
    ).execute()
    IoC[ICommand].resolve(
        'IoC.Dependency.Register', 'IMovingObjMock.location.Get', lambda obj: obj.get_value('location')
    ).execute()
    IoC[ICommand].resolve(
        'IoC.Dependency.Register',
        'IMovingObjMock.location.Set',
        lambda obj, value: SetLocationCommand(obj, 'location', value)
    ).execute()
    mock_obj: MockGameItem = IoC.resolve('MockGameItem')

    mock_obj.add_property('location', 12345)
    adapter_obj = IoC.resolve('Adapter', IMovingObjMock, mock_obj)

    adapter_obj.location = 9876

    assert adapter_obj.location == 9876


def test_making_generated_method() -> None:
    """Получение сгенерированного метода объекта."""

    InitCommand().execute()
    IoC[ICommand].resolve(
        'IoC.Dependency.Register', 'MockGameItem', lambda *args: MockGameItem()
    ).execute()
    IoC[ICommand].resolve(
                'IoC.Dependency.Register',
                'IMovingObj.Method.return_string',
                lambda obj: obj.return_string()
            ).execute()

    mock_obj: MockGameItem = IoC.resolve('MockGameItem')

    result = mock_obj.return_string()
    expected_result = 'string'

    assert result == expected_result
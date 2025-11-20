from typing import TypeVar, Generic, Any

from interfaces import IAdapterFactory, IMovingObj
from ioc import IoC, InitCommand

T = TypeVar('T')


class SpaceShip(IMovingObj):
    def __init__(self, location):
        self._location = location

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value


class DynamicAdapterFactory(Generic[T]):

    def create_adapter_factory(self) -> IAdapterFactory:
        """Динамически создает фабрику адаптеров."""

        interface_type: T = self.__orig_class__.__args__[0]  # type: ignore
        interface_name: str = interface_type.__name__  # Название объекта T

        adapter_class_name = interface_name[1:] + 'Adapter'  # T = IMovingObj => MovingObjAdapter
        factory_class_name = adapter_class_name + 'Factory'  # MovingObjAdapterFactory

        # |-------------------------------------------|
        #     Динамическое создание класса адаптера
        # |-------------------------------------------|

        adapter_attrs = {}

        for attr_name, attr_value in interface_type.__dict__.items():

            if isinstance(attr_value, property):
                getter_ioc_key = f"{interface_name}.{attr_name}.Get"
                setter_ioc_key = f"{interface_name}.{attr_name}.Set"
                deleter_ioc_key = f"{interface_name}.{attr_name}.Del"

                def make_getter(key: str):
                    return lambda self: IoC[Any].resolve(key, self._obj)

                def make_setter(key: str):
                    return lambda self, value: IoC[Any].resolve(key, self._obj, value).execute()

                def make_deleter(key: str):
                    return lambda self: IoC[Any].resolve(key, self._obj).execute()

                adapter_attrs[attr_name] = property(
                    make_getter(getter_ioc_key), make_setter(setter_ioc_key), make_deleter(deleter_ioc_key)
                )

            elif getattr(attr_value, "__isabstractmethod__", False):

                def make_method(method_name: str):
                    return lambda self, *args, **kwargs: IoC.resolve(
                        f"{interface_name}.{method_name}", self._obj, *args, **kwargs
                    )

                adapter_attrs[attr_name] = make_method(attr_name)

        def adapter_init(self, obj):
            self._obj = obj

        adapter_attrs["__init__"] = adapter_init

        adapter_class = type(adapter_class_name, (), adapter_attrs)

        # |-------------------------------------------|
        #    Динамическое создание фабрики адаптера
        # |-------------------------------------------|

        adapter_factory_class = type(
            factory_class_name,
            (IAdapterFactory,),
            {"create": lambda self, obj: adapter_class(obj)}
        )

        return adapter_factory_class()


if __name__ == '__main__':
    InitCommand().execute()
    factory = DynamicAdapterFactory[IMovingObj]().create_adapter_factory()  # MovingObjAdapterFactory ->
    obj = factory.create(SpaceShip(1234))
    obj.location = 5
    print(obj.location)
    # разрешать зависимости нужно так IoC[IGameItem].resolve('Factory')
    # print(obj)

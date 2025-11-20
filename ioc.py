from typing import TypeVar, Generic, NoReturn, Type
from collections.abc import Callable
from typing import Any
import threading

from interfaces import ICommand, IResolver

T = TypeVar('T')


class UpdateIoCStrategy(ICommand):
    def __init__(self, strategy: Callable[[str, Any], T]) -> None:
        self.strategy = strategy

    def execute(self) -> None:
        IoC._strategy = self.strategy


class RegisterDependencyCommand(ICommand):
    def __init__(self, dependency: str, strategy: Callable) -> None:
        self.dependency = dependency
        self.strategy = strategy

    def execute(self) -> None:
        current_scope = IoC[dict].resolve('IoC.Scope.Current')
        current_scope[self.dependency] = self.strategy


class DependencyResolver(IResolver):

    def __init__(self, root_scope: dict, current_scope: threading.local) -> None:
        self.root_scope = root_scope
        self.current_scope = current_scope

    def resolve(self, dependency: str, *args) -> Callable:

        try:
            scope = self.current_scope.value
        except AttributeError:
            scope = self.root_scope

        while True:
            depend = scope.get(dependency)
            if depend:
                return depend(*args)
            try:
                scope = scope['IoC.Scope.Parent'](*args)
            except ValueError:
                raise ValueError(f'Зависимость {dependency} не найдена!')


class InitCommand(ICommand):
    root_scope = {}
    current_scope = threading.local()

    _lock = threading.RLock()
    _is_executed = False

    def execute(self) -> None:
        if self._is_executed:
            return

        with self._lock:
            self.root_scope['IoC.Scope.Empty'] = lambda *args: {}
            self.root_scope['IoC.Scope.Create'] = lambda *args: self.create_new_scope(*args)
            self.root_scope['IoC.Scope.Current'] = lambda *args: self.get_current_scope()
            self.root_scope['IoC.Scope.Current.Set'] = lambda *args: self.set_current_scope(args[0])
            self.root_scope['IoC.Scope.Parent'] = lambda *args: self.get_parent_scope()
            self.root_scope['IoC.Dependency.Register'] = lambda *args: RegisterDependencyCommand(args[0], args[1])
            self.root_scope['IoC.Scope.Root.Get'] = lambda *args: self.root_scope
            self.root_scope['IoC.Scope.Current.Get'] = lambda *args: self.current_scope
            self.root_scope['Adapter'] = lambda *args: self.get_adapter(args[0], args[1])

            IoC[ICommand].resolve('UpdateIoCStrategy',
                                  DependencyResolver(self.root_scope, self.current_scope).resolve).execute()

        self._is_executed = True

    def create_new_scope(self, *args) -> dict:
        new_scope = IoC[dict].resolve('IoC.Scope.Empty')

        if args:
            parent_scope = args[0]
        else:
            parent_scope = IoC[dict].resolve('IoC.Scope.Current')
        new_scope['IoC.Scope.Parent'] = lambda *args: parent_scope

        return new_scope

    def get_current_scope(self):
        try:
            return self.current_scope.value
        except AttributeError:
            return self.root_scope

    def set_current_scope(self, scope: dict) -> None:
        self.current_scope.value = scope

    def get_parent_scope(self) -> NoReturn:
        raise ValueError('Root scope have no parent scope')

    def get_adapter(self, interface: Type[Any], obj: Any):
        from adapter import DynamicAdapterFactory
        adapter_factory = DynamicAdapterFactory[interface]().create_adapter_factory()
        return adapter_factory.create(obj)


class IoC(Generic[T]):
    _strategy: Callable[[str, Any], T]

    @classmethod
    def resolve(cls, dependency: str, *args) -> T:
        if dependency == 'UpdateIoCStrategy':
            return UpdateIoCStrategy(args[0])
        return cls._strategy(dependency, *args)

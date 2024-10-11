from typing import Type, TypeVar, Callable
from ..routes import Controller

T = TypeVar("T", bound="Controller")


def controller(base_path: str = "") -> Callable[[Type[T]], Type[T]]:
    """Decorator to attach a base path to a controller class."""

    def class_decorator(cls: Type[T]) -> Type[T]:
        setattr(cls, "_base_path", base_path)

        return cls

    return class_decorator

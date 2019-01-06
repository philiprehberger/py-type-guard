"""Runtime type checking decorators for function arguments."""

from __future__ import annotations

import functools
import inspect
import types
import typing
from typing import Any, Callable, Union, get_args, get_origin


__all__ = [
    "guard",
    "TypeGuardError",
    "enable",
    "disable",
]

_enabled: bool = True


class TypeGuardError(TypeError):
    """Raised when a function argument does not match its type hint."""

    def __init__(self, param: str, expected: type | str, actual: type, value: Any) -> None:
        self.param = param
        self.expected = expected
        self.actual = actual
        self.value = value
        expected_name = expected if isinstance(expected, str) else getattr(expected, "__name__", str(expected))
        super().__init__(
            f"Parameter '{param}' expected {expected_name}, "
            f"got {actual.__name__} (value: {value!r})"
        )


def enable() -> None:
    """Enable runtime type checking globally."""
    global _enabled
    _enabled = True


def disable() -> None:
    """Disable runtime type checking globally."""
    global _enabled
    _enabled = False


def guard(
    fn: Callable[..., Any] | None = None,
    *,
    enabled: bool = True,
) -> Any:
    """Decorator that validates function arguments against type hints at runtime.

    Can be used as ``@guard`` or ``@guard(enabled=True)``.

    Args:
        fn: The function to decorate (when used without parentheses).
        enabled: Whether this specific guard is active.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        hints = typing.get_type_hints(func)
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _enabled or not enabled:
                return func(*args, **kwargs)

            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for param_name, value in bound.arguments.items():
                if param_name == "return":
                    continue
                if param_name not in hints:
                    continue

                annotation = hints[param_name]
                if not _check_type(value, annotation):
                    raise TypeGuardError(
                        param=param_name,
                        expected=_type_name(annotation),
                        actual=type(value),
                        value=value,
                    )

            return func(*args, **kwargs)

        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


def _check_type(value: Any, annotation: Any) -> bool:
    if annotation is Any:
        return True

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union or origin is types.UnionType:
        return any(_check_type(value, arg) for arg in args)

    if annotation is type(None):
        return value is None

    if origin is None:
        if isinstance(annotation, type):
            return isinstance(value, annotation)
        return True

    if origin is list:
        if not isinstance(value, list):
            return False
        if args:
            return all(_check_type(item, args[0]) for item in value)
        return True

    if origin is dict:
        if not isinstance(value, dict):
            return False
        if args and len(args) == 2:
            return all(
                _check_type(k, args[0]) and _check_type(v, args[1])
                for k, v in value.items()
            )
        return True

    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if args:
            if len(args) == 2 and args[1] is Ellipsis:
                return all(_check_type(item, args[0]) for item in value)
            if len(args) == len(value):
                return all(_check_type(v, a) for v, a in zip(value, args))
            return False
        return True

    if origin is set:
        if not isinstance(value, set):
            return False
        if args:
            return all(_check_type(item, args[0]) for item in value)
        return True

    if origin is frozenset:
        if not isinstance(value, frozenset):
            return False
        if args:
            return all(_check_type(item, args[0]) for item in value)
        return True

    if isinstance(origin, type):
        return isinstance(value, origin)

    return True


def _type_name(annotation: Any) -> str:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union or origin is types.UnionType:
        return " | ".join(_type_name(a) for a in args)

    if hasattr(annotation, "__name__"):
        name = annotation.__name__
    elif hasattr(annotation, "_name"):
        name = annotation._name
    else:
        name = str(annotation)

    if args:
        arg_names = ", ".join(_type_name(a) for a in args)
        return f"{name}[{arg_names}]"

    return name

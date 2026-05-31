import pytest
from philiprehberger_type_guard import (
    guard,
    TypeGuardError,
    enable,
    disable,
    is_type,
    assert_type,
)


def test_valid_types():
    @guard
    def greet(name: str, count: int) -> str:
        return name * count

    assert greet("hi", 2) == "hihi"


def test_invalid_type_raises():
    @guard
    def greet(name: str) -> str:
        return name

    with pytest.raises(TypeGuardError):
        greet(123)


def test_error_details():
    @guard
    def fn(x: int):
        pass

    try:
        fn("hello")
    except TypeGuardError as e:
        assert e.param == "x"
        assert e.actual is str
        assert e.value == "hello"


def test_optional_type():
    @guard
    def fn(x: int | None):
        return x

    assert fn(42) == 42
    assert fn(None) is None
    with pytest.raises(TypeGuardError):
        fn("bad")


def test_list_generic():
    @guard
    def fn(items: list[int]):
        return items

    assert fn([1, 2, 3]) == [1, 2, 3]
    with pytest.raises(TypeGuardError):
        fn(["a", "b"])


def test_dict_generic():
    @guard
    def fn(data: dict[str, int]):
        return data

    assert fn({"a": 1}) == {"a": 1}
    with pytest.raises(TypeGuardError):
        fn({1: "a"})


def test_disable_enable():
    @guard
    def fn(x: int):
        return x

    disable()
    assert fn("not an int") == "not an int"

    enable()
    with pytest.raises(TypeGuardError):
        fn("not an int")


def test_guard_with_defaults():
    @guard
    def fn(x: int = 5):
        return x

    assert fn() == 5
    assert fn(10) == 10


def test_no_annotations_skipped():
    @guard
    def fn(x):
        return x

    assert fn("anything") == "anything"


def test_is_type_simple():
    assert is_type(5, int) is True
    assert is_type("x", int) is False


def test_is_type_list_generic():
    assert is_type([1, 2], list[int]) is True
    assert is_type([1, "x"], list[int]) is False


def test_is_type_optional():
    assert is_type(None, int | None) is True
    assert is_type(0, int | None) is True
    assert is_type("x", int | None) is False


def test_assert_type_passes_silently():
    assert assert_type(5, int) is None


def test_assert_type_raises_with_default_name():
    with pytest.raises(TypeGuardError) as exc_info:
        assert_type("x", int)
    message = str(exc_info.value)
    assert "int" in message
    assert "value" in message


def test_assert_type_raises_with_custom_name():
    with pytest.raises(TypeGuardError) as exc_info:
        assert_type("x", int, name="my_arg")
    message = str(exc_info.value)
    assert "int" in message
    assert "my_arg" in message


def test_assert_type_respects_disable():
    disable()
    try:
        assert_type("x", int)
    finally:
        enable()

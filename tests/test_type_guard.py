import pytest
from philiprehberger_type_guard import guard, TypeGuardError, enable, disable


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

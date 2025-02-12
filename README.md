# philiprehberger-type-guard

[![Tests](https://github.com/philiprehberger/py-type-guard/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-type-guard/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-type-guard.svg)](https://pypi.org/project/philiprehberger-type-guard/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-type-guard)](https://github.com/philiprehberger/py-type-guard/commits/main)

Runtime type checking decorators for function arguments.

## Installation

```bash
pip install philiprehberger-type-guard
```

## Usage

### Basic Usage

```python
from philiprehberger_type_guard import guard

@guard
def greet(name: str, times: int = 1) -> str:
    return name * times

greet("hello", 3)     # Works fine
greet(123, 3)          # Raises TypeGuardError
```

### Generic Types

```python
@guard
def process(items: list[int], lookup: dict[str, float]):
    ...

process([1, 2, 3], {"a": 1.0})  # OK
process(["a"], {})               # TypeGuardError
```

### Union Types

```python
@guard
def flexible(value: int | str | None):
    ...

flexible(42)     # OK
flexible("hi")   # OK
flexible(None)   # OK
flexible(3.14)   # TypeGuardError
```

### Global Toggle

```python
from philiprehberger_type_guard import enable, disable

disable()  # Turn off all guards (e.g., in production)
enable()   # Turn back on
```

### Error Details

```python
from philiprehberger_type_guard import TypeGuardError

try:
    greet(123, 3)
except TypeGuardError as e:
    print(e.param)     # "name"
    print(e.expected)  # "str"
    print(e.actual)    # <class 'int'>
    print(e.value)     # 123
```

## API

| Function / Class | Description |
|------------------|-------------|
| `@guard` / `@guard(enabled=True)` | Decorator for runtime type checking |
| `enable()` / `disable()` | Global toggle |
| `TypeGuardError` | Raised on type mismatch (subclass of `TypeError`) |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-type-guard)

🐛 [Report issues](https://github.com/philiprehberger/py-type-guard/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-type-guard/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)

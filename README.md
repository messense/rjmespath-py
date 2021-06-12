# rjmespath-py

![CI](https://github.com/messense/rjmespath-py/workflows/CI/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/rjmespath.svg)](https://pypi.org/project/rjieba)

[jmespath.rs](https://github.com/jmespath/jmespath.rs) Python binding.

## Installation

```bash
pip install rjmespath
```

## Usage

```python
import rjmespath

print(rjmespath.search('foo.bar', '{"foo": {"bar": "baz"}}'))
```

## License

This work is released under the MIT license. A copy of the license is provided in the [LICENSE](./LICENSE) file.

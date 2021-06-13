# rjmespath-py

![CI](https://github.com/messense/rjmespath-py/workflows/CI/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/rjmespath.svg)](https://pypi.org/project/rjmespath)

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

## Performance

Running on MacBook Pro (13-inch, M1, 2020, 16GB RAM)

```python
In [1]: import jmespath

In [2]: import rjmespath

In [3]: %timeit jmespath.compile('foo')
436 ns ± 0.478 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [4]: %timeit rjmespath.compile('foo')
354 ns ± 0.583 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [5]: %timeit jmespath.search('foo.bar', {"foo": {"bar": "baz"}})
2.74 µs ± 10.1 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

In [6]: %timeit rjmespath.search('foo.bar', '{"foo": {"bar": "baz"}}')
1.21 µs ± 12.3 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
```

## License

This work is released under the MIT license. A copy of the license is provided in the [LICENSE](./LICENSE) file.

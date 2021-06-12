import os
import json

import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLIANCE_DIR = os.path.join(TEST_DIR, "compliance")


def _walk_files():
    # Check for a shortcut when running the tests interactively.
    # If a JMESPATH_TEST is defined, that file is used as the
    # only test to run.  Useful when doing feature development.
    single_file = os.environ.get("JMESPATH_TEST")
    if single_file is not None:
        yield os.path.abspath(single_file)
    else:
        for root, dirnames, filenames in os.walk(TEST_DIR):
            for filename in filenames:
                yield os.path.join(root, filename)


def load_cases(full_path):
    all_test_data = json.load(open(full_path, encoding="utf-8"))
    for test_data in all_test_data:
        given = json.dumps(test_data["given"])
        for case in test_data["cases"]:
            if "result" in case:
                test_type = "result"
            elif "error" in case:
                test_type = "error"
            elif "bench" in case:
                test_type = "bench"
            else:
                raise RuntimeError("Unknown test type: %s" % json.dumps(case))
            yield (given, test_type, case)


result_cases = []
error_cases = []
for full_path in _walk_files():
    if full_path.endswith(".json"):
        for given, test_type, test_data in load_cases(full_path):
            t = test_data
            # Benchmark tests aren't run as part of the normal
            # test suite, so we only care about 'result' and
            # 'error' test_types.
            if test_type == "result":
                result_cases.append(
                    (given, t["expression"], t["result"], os.path.basename(full_path))
                )
            elif test_type == "error":
                error_cases.append(
                    (given, t["expression"], t["error"], os.path.basename(full_path))
                )


@pytest.mark.parametrize("given, expression, expected, filename", result_cases)
def test_expression(given, expression, expected, filename):
    import rjmespath

    try:
        parsed = rjmespath.compile(expression)
    except ValueError as e:
        raise AssertionError(
            'jmespath expression failed to compile: "%s", error: %s"' % (expression, e)
        )
    actual = parsed.search(given)
    expected_repr = json.dumps(expected, indent=4)
    actual_repr = json.dumps(actual, indent=4)
    error_msg = (
        "\n\n  (%s) The expression '%s' was suppose to give:\n%s\n"
        "Instead it matched:\n%s\ngiven:\n%s"
        % (
            filename,
            expression,
            expected_repr,
            actual_repr,
            json.dumps(given, indent=4),
        )
    )
    error_msg = error_msg.replace(r"\n", "\n")
    assert actual == expected, error_msg


@pytest.mark.parametrize("given, expression, error, filename", error_cases)
def test_error_expression(given, expression, error, filename):
    import rjmespath

    if error not in (
        "syntax",
        "invalid-type",
        "unknown-function",
        "invalid-arity",
        "invalid-value",
    ):
        raise RuntimeError("Unknown error type '%s'" % error)
    try:
        parsed = rjmespath.compile(expression)
        parsed.search(given)
    except ValueError:
        # Test passes, it raised a parse error as expected.
        pass
    except Exception as e:
        # Failure because an unexpected exception was raised.
        error_msg = (
            "\n\n  (%s) The expression '%s' was suppose to be a "
            "syntax error, but it raised an unexpected error:\n\n%s"
            % (filename, expression, e)
        )
        error_msg = error_msg.replace(r"\n", "\n")
        raise AssertionError(error_msg)
    else:
        error_msg = (
            "\n\n  (%s) The expression '%s' was suppose to be a "
            "syntax error, but it successfully" % (filename, expression)
        )
        error_msg = error_msg.replace(r"\n", "\n")
        raise AssertionError(error_msg)

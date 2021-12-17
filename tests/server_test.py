import pytest


@pytest.mark.parametrize("my_input, expected", [
    (1, 1),
    ("1", 1),
    ("one", False),
    (0j + 1, 1),
    (1j + 1, False),
    (1.4, False),
    ("1.4", False),
    ("12a", False),
    ("123", 123)
])
def test_intify(my_input, expected):
    from server import try_intify
    answer = try_intify(my_input)
    assert answer == expected


@pytest.mark.parametrize("my_input, expected", [
    (1.0, 1.0),
    ("1", 1.0),
    ("one", False),
    (0j + 1, 1.0),
    (1j + 1, False),
    (1.4, 1.4),
    ("12a", False),
    ("123.3", 123.3)
])
def test_floatify(my_input, expected):
    from server import try_floatify
    answer = try_floatify(my_input)
    assert answer == expected


@pytest.mark.parametrize("my_input, exp_in, exp_out", [
    ({"a": 1, "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     (True, 200)),
    ({"ab": 1, "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     ("the key a is missing from the input", 400)),
    ({"a": "1", "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     ("the key 'a' is a <class 'str'>, should be <class 'int'>", 400)),
    ({"a": 1.4, "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     ("the key 'a' is a <class 'float'>, should be <class 'int'>", 400)),
    ([], {"a": int, "b": str, "c": float},
     ("The input was not a dictionary.", 400))
])
def test_inputs(my_input, exp_in, exp_out):
    from server import validate_input
    answer = validate_input(my_input, exp_in)
    assert answer == exp_out

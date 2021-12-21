import os

import pytest

import server as serv

filename = os.path.join("tests", "b64.txt")
with open(filename, "r") as fobj:
    b64_str = fobj.read()
type_keys = {"a": int, "b": float, "c": str, "d": list}


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
    answer = serv.try_intify(my_input)
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
    answer = serv.try_floatify(my_input)
    assert answer == expected


@pytest.mark.parametrize("my_input, exp_in, exp_out", [
    ({"a": 1, "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     (True, 200)),
    ({"ab": 1, "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     (True, 200)),
    ({"a": "1", "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     ("the key 'a' is a <class 'str'>, should be <class 'int'>", 400)),
    ({"a": 1.4, "b": "Smith.J", "c": 50.2}, {"a": int, "b": str, "c": float},
     ("the key 'a' is a <class 'float'>, should be <class 'int'>", 400)),
    ([], {"a": int, "b": str, "c": float},
     ("The input was not a dictionary.", 400))
])
def test_inputs(my_input, exp_in, exp_out):
    answer = serv.validate_input(my_input, exp_in)
    assert answer == exp_out


def test_rendering():
    expected = """<h1>Ann Ables<h1>
    <img src='data:image/png;base64,{}'
        alt='img_data'  id='imgslot'/>""".format(b64_str)
    with serv.app.app_context():
        answer = serv.render_image(b64_str, "Ann Ables")
    assert answer == expected


@pytest.mark.parametrize("my_in, types, expected", [
    ({"a": "1", "b": "1.1", "c": "word", "d": ["1"]}, type_keys,
     {"a": 1, "b": 1.1, "c": "word", "d": ["1"]}),
    ({"a": "1.1"}, type_keys, "key a is not convertable to an integer"),
    ({"b": "one"}, type_keys, "key b is not convertable to a float")
])
def test_correction(my_in, types, expected):
    from server import correct_input
    answer = correct_input(my_in, types)
    assert answer == expected

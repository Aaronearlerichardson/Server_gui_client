import pytest
with open("b64.txt", "r") as fobj:
    b64_str = fobj.read()
import server as serv
import database as db


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
     ("the key a is missing from the input", 400)),
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
    <img src='data:image/jpeg;base64,{}' 
        alt='img_data'  id='imgslot'/>""".format(b64_str)
    with serv.app.app_context():
        answer = serv.render_image(b64_str, "Ann Ables")
    assert answer == expected


@pytest.mark.parametrize("terms, db_input, expected", [
    ({"a": 1}, [{'a': 1}, {"a": 2}], {'a': 1}),
    ({"a": 2}, [{'a': 1}], "No a with the value 2"
                           " found in Database database"),
    ({"b": 1}, [{'a': 1}], "No b with the value 1 "
                           "found in Database database"),
    ({"a": 1, "b": 2}, [{"a": 1}], {"a": 1}),
    ({"a": 1, "b": 2}, [{"a": 1, "b": 3}, {"a": 4, "b": 2}],
     {"a": 4, "b": 2}),
    ({"get": "all", "a": 1, "b": 2}, [{"a": 1, "b": 3}, {"a": 4, "b": 2}],
     [{"a": 1, "b": 3}, {"a": 4, "b": 2}]),
    ({"get": "first", "a": 1},
     [{"a": 1, "b": 3}, {"a": 1, "b": 2}, {"a": 4, "b": 2}],
     {"a": 1, "b": 3}),
    ({"get": "latest", "a": 1},
     [{"a": 1, "b": 3}, {"a": 1, "b": 2}, {"a": 4, "b": 2}],
     {"a": 1, "b": 2}),
    ({"get": "first", "a": 1, "b": 2},
     [{"a": 1, "b": 3}, {"a": 1, "b": 2}, {"a": 4, "b": 2}],
     {"a": 1, "b": 3}),
    ({"get": "latest", "a": 1, "b": 2},
     [{"a": 1, "b": 3}, {"a": 1, "b": 2}, {"a": 4, "b": 2}],
     {"a": 4, "b": 2}),
    ({"get": "all", "a": 1, "b": 2}, [{"a": 1, "b": 3}, {"a": 4, "b": 6}],
     [{"a": 1, "b": 3}]),
    ({"get": "all", "a": 1, "b": 2}, [{"a": 2, "b": 3}, {"a": 4, "b": 1}],
     "No a or b with the value 1 or 2 found in Database database"),
    ({"a": 1, "b": 2}, [{"b": 2}], {"b": 2}),
    ({"a": 1, "b": 2}, [{"c": 3}], "No a or b with the value 1 or 2 found in "
                                   "Database database"),
    ({"a": 1, "b": 2}, [{"b": "2"}], "No a or b with the value 1 or 2 found in"
                                     " Database database"),
    ({"1": 2}, [{1: 2}], "No 1 with the value 2 found in Database database"),
    ({"a": 1}, [{"a": 1, "b": 2}], {"a": 1, "b": 2}),
    ({"get": "all", "a": 1}, [{'a': 1}], [{'a': 1}]),
    ({"get": "all", "a": 1}, [{'a': 1}, {"a": 2}], [{'a': 1}]),
    ({"get": "all", "a": 1}, [{'a': 1, "b": 1}, {"a": 1, "b": 2}],
     [{'a': 1, "b": 1}, {"a": 1, "b": 2}])
])
def test_database_search(terms, db_input, expected):
    my_db = db.Database(*db_input)
    try:
        answer = my_db.search(**terms)
    except IndexError as e:
        answer = e.__str__()
    assert answer == expected


temp_db = db.Database()
sample = {"patient_id": 1, "heart_rate": 100}


@pytest.mark.parametrize("my_in, kwargs, out, tot_out", [
    (sample, {}, sample, [sample]),
    (sample, {"time": "noon"},
     {"patient_id": 1, "heart_rate": 100, "time": "noon"},
     [sample, {"patient_id": 1, "heart_rate": 100, "time": "noon"}])
])
def test_database_add_entry(my_in, kwargs, out, tot_out):
    answer = temp_db.add_entry(my_in, **kwargs)
    assert answer == out
    assert temp_db == tot_out

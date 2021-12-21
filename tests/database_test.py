import pytest

import database as db

temp_db = db.Database()
index_db = db.Database(index="a")


@pytest.mark.parametrize("my_in, kwargs, in_db, out, tot_out", [
    ({"a": 1, "b": 100}, {}, temp_db, {"a": 1, "b": 100},
     [{"a": 1, "b": 100}]),
    ({"a": 1, "b": 100}, {"time": "noon"},  temp_db,
     {"a": 1, "b": 100, "time": "noon"},
     [{"a": 1, "b": 100}, {"a": 1, "b": 100, "time": "noon"}]),
    ({"a": 1, "b": 100}, {}, index_db, {"a": 1, "b": 100},
     [{"a": 1, "b": 100}]),
    ({"a": 1, "b": 100}, {"times": ["noon"]},  index_db,
     {"a": 1, "b": 100, "times": ["noon"]},
     [{"a": 1, "b": 100, "times": ["noon"]}]),
    ({"a": 1, "b": 100}, {"times": ["morning"]}, index_db,
     {"a": 1, "b": 100, "times": ["noon", "morning"]},
     [{"a": 1, "b": 100, "times": ["noon", "morning"]}]),
    ({"a": 2, "times": ["night"]}, {}, index_db,
     {"a": 2, "times": ["night"]},
     [{"a": 1, "b": 100, "times": ["noon", "morning"]},
      {"a": 2, "times": ["night"]}]),
    ({"a": 2, "b": 90}, {}, index_db,
     {"a": 2, "b": 90, "times": ["night"]},
     [{"a": 1, "b": 100, "times": ["noon", "morning"]},
      {"a": 2, "b": 90, "times": ["night"]}])
])
def test_database_add_entry(my_in, kwargs, in_db, out, tot_out):
    answer = in_db.add_entry(my_in, **kwargs)
    assert answer == out
    assert in_db == tot_out


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

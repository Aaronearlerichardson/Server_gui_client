import logging
import os

import numpy as np
import pandas as pd
import pytest
import scipy.signal as sig
from testfixtures import LogCapture

from ecg_analysis import ecg_reader as erd

logging.basicConfig(level=logging.INFO)
data_1 = pd.DataFrame.from_dict(
    dict(time=list(range(7)), voltage=[-1, float("nan"), 200, "",
                                       "0.2", "bad", "0.7"]))
data_1.name = "data"
data_2 = pd.DataFrame.from_dict(
    dict(time=[0.0, 2.0, 4.0, 6.0], voltage=[-1, 200, 0.2, 0.7]))
data_2.name = "data"

# generate ecg https://stackoverflow.com/questions/4387878/
rr = [1.0, 1.0, 0.5, 1.5, 1.0, 1.0]  # rr time in seconds
fs = 2000.0  # sampling rate
pqrst = sig.wavelets.daub(10)  # just to simulate a signal, whatever
ecg = np.concatenate([sig.resample(pqrst, int(r * fs)) for r in rr])
t = np.arange(len(ecg)) / fs
ecg = np.reshape(ecg, (1, len(ecg)))


@pytest.mark.parametrize("input_1, input_2, input_3, input_4, expected", [
    (pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -1]), "file", 9.5, 0,
     ("root", "ERROR", "data point 9 in file has a value higher than 9.5")),
    (pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 10]), "file", 9.5, 0,
     ("root", "ERROR", "data point 9 in file has a value lower than 0")),
    (pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9]), "file", 9.5, 0, False)
])
def test_check_range(input_1, input_2, input_3, input_4, expected):
    with LogCapture() as log_c:
        erd.check_range(input_1, input_2, input_3, input_4)
    if expected:
        log_c.check(expected)
    else:
        log_c.check()


def test_clean_data():
    with LogCapture() as log_c:
        answer = erd.clean_data(data_1)
    answer.reset_index(drop=True, inplace=True)
    log_c.check(('root', 'ERROR', 'removed non-numeric data from data at '
                                  'line 6 out of 7 data points'),
                ('root', 'ERROR', 'removed nan data from data at line 2 '
                                  'out of 7 data points'),
                ('root', 'ERROR', 'removed missing data from data at line 4'
                                  ' out of 7 data points'))
    print(answer, data_2)
    assert answer.equals(data_2)


def test_filter():
    # add noise to data
    noise = []
    for item in ecg[0]:
        noise.append(item + (np.random.ranf() - 0.5) / 2)
    my_series = pd.Series(noise).astype(float)
    answer = erd.filter_data(my_series, t[0], t[-1], 6, 1)
    mse = sum(np.subtract(answer[0], ecg[0]) ** 2) / len(answer[0])
    assert mse <= 0.01


def test_preprocess():
    expected = erd.clean_data(
        erd.load_csv(os.path.join("ecg_analysis", "tests",
                                  "test_data1_orig.csv"), ["time", "voltage"]))
    with LogCapture() as log_c:
        answer = erd.preprocess_data(
            os.path.join("test_data", "test_data1.csv"),
            raw_max=300,
            l_freq=1,
            h_freq=50)
    log_c.check()
    mse = sum(np.subtract(answer["voltage"],
                          expected["voltage"]) ** 2) / len(answer)
    assert mse <= 0.01


@pytest.mark.parametrize("input_1, expected", [
    ("28.6", True),
    (28, True),
    (28.6, True),
    (28.6 + 0j, True),  # complex number
    (28.6 + 1j, False),  # complex number
    ("twenty-eight point two", False),
    ("NaN", True),  # NaN is a number
    ("NANANANANANANANANAN BATMAAAAAAN", False),
    ("", False),
    (True, False),
    (False, False)
])
def test_is_num(input_1, expected):
    answer = erd.is_num(input_1)
    assert answer == expected


@pytest.mark.parametrize("input_1, expected", [
    ("28.6", False),
    (28, False),
    (28.6, False),
    ("twenty-eight point two", False),
    ("NaN", True),  # NaN
    (float("nan"), True),
    ("NANANANANANANANANAN BATMAAAAAAN", False),
    ("", False),
    (False, False)
])
def test_is_nan(input_1, expected):
    answer = erd.is_nan(input_1)
    assert answer == expected


@pytest.mark.parametrize("input_1, expected", [
    ("28.6", False),
    (28, False),
    (28.6, False),
    ("twenty-eight point two", False),
    ("NaN", False),  # NaN
    (float("nan"), False),
    ("NANANANANANANANANAN BATMAAAAAAN", False),
    ("", True),
    (str(""), True),
    ([], False),
    ((), False),
    ({}, False),
    (False, False),
    (" ", False),
    (" ".strip(), True)
])
def test_is_mt(input_1, expected):
    answer = erd.is_mt_str(input_1)
    assert answer == expected


@pytest.mark.parametrize("data, func, invert, expected1, expected2", [
    (data_1.drop([3, 5]).astype(float), np.isnan, True, data_2, [1]),
    (pd.DataFrame(["joey", "Obama", "AARON"]), np.char.islower, False,
     pd.DataFrame(["joey"]), [1, 2]),
    (data_1, erd.is_nan, True, data_1.drop([1]), [1]),
    (data_1.drop([1]), erd.is_num, False, data_1.drop([1, 3, 5]), [3, 5]),
    (data_1.drop([1]), erd.is_mt_str, True, data_1.drop([1, 3]), [3])
])
def test_apply(data, func, invert, expected1, expected2):
    answer, indices = erd.apply_to_df(data, func, invert)
    answer = answer.reset_index(drop=True)
    expected1 = expected1.reset_index(drop=True)
    assert expected1.eq(answer).all(1).all(0)
    assert indices.tolist() == expected2

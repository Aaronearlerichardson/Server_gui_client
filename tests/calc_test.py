import pytest
from pandas import DataFrame
from testfixtures import LogCapture

import calculations as calc
from tests.reader_test import ecg, t

ecg_df = DataFrame().from_dict({"time": t.tolist(),
                                "voltage": ecg[0].tolist()})
ecg_df.name = "test"


@pytest.mark.parametrize("input_1, expected", [
    (ecg_df, dict(duration=6.0,
                  extremes=(0.698, -0.308),
                  filename='test',
                  mean_hr_bpm=40.0,
                  num_beats=4,
                  beats=[1.1415, 2.071, 4.1415, 5.1415]))
])
def test_metrics(input_1, expected):
    with LogCapture() as log_c:
        answer = calc.get_metrics(input_1)
    assert answer == expected
    log_c.check(('root', 'INFO', 'For file: ' + expected["filename"]),
                ('root', 'INFO',
                 'The duration was {}'.format(expected["duration"])),
                ('root', 'INFO', 'The {} extremes were {}'.format(
                    "voltage", expected["extremes"])),
                ('root', 'INFO', 'The beat times were [' + ", ".join(
                    [str(i) for i in expected["beats"]]) + "]"),
                ('root', 'INFO', 'The number of beats was {}'.format(
                    expected["num_beats"])),
                ('root', 'INFO', 'The mean heart rate was {} bpm'.format(
                    expected["mean_hr_bpm"])))

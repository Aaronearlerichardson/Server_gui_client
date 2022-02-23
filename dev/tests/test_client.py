import os
import pytest
from typing import List
import tempfile
import dev.defaults as defaults


default_data = defaults.DefaultData()


@pytest.mark.parametrize("dataset, subjects", [
    ("ds003029", ["pt01", "jh101"]),
    ("ds003029", ["pt2"])
])
def test_download_data(dataset: str, subjects: List[str]):
    from dev.client import download_data
    with tempfile.TemporaryDirectory() as tempdir:

        # run data downloader
        answer = download_data(dataset, subjects, tempdir)

        # check
        assert tempdir == answer.root
        assert not len(os.listdir(answer.root)) == 0


@pytest.mark.parametrize("inputs, expected", [
    ({}, {"scope": "raw", "suffix": "ieeg", "extension": "vhdr"}),
    (None, {"scope": "raw", "suffix": "ieeg", "extension": "vhdr"}),
    ({"extension": "edf"},
     {"scope": "raw", "suffix": "ieeg", "extension": "edf"}),
    ({"runs": 1},
     {"scope": "raw", "suffix": "ieeg", "extension": "vhdr", "runs": 1})
])
def test_layout_defaults(inputs, expected):
    answer = defaults.layout(inputs)
    assert answer == expected


def test_bids_to_raw():
    from dev.client import bids_to_raw
    raw = bids_to_raw(default_data.file)
    assert default_data.raw == raw


def test_layout_to_raw_dict():
    from dev.client import layout_to_raw_dict
    expected = {"pt1": {1: default_data.raw}}
    answer = layout_to_raw_dict(default_data.layout)
    assert answer == expected

import pytest
import mne
from dev.eeg_final import pat_data
from dev.tests.test_client import default_data
import os.path as op
from testfixtures import LogCapture


@pytest.mark.parametrize("my_input, output", [
    ({}, ("The input was not a correct file type", 400)),
    ({"file": "urmom"}, (True, 200))
])
def test_validate_file_input(my_input, output):
    from dev.eeg_final import validate_file_input
    answer = validate_file_input(my_input)
    assert answer == output


# @pytest.mark.parametrize("my_input, exp_database", [
#    (defaults.raw, {"pt1": {1: defaults.raw}}),
#    ])
def test_databasing():  # raw, exp_database):
    from dev.eeg_final import databasing

    # adding first file to db
    default_data.raw.save("raw_ieeg.fif", overwrite=True)
    raw1 = mne.io.read_raw_fif("raw_ieeg.fif", preload=True)
    databasing("raw_ieeg.fif")
    time1 = '07/24/1920, 19:35:19'
    pat_data["sub-pt1"][time1].load_data()
    assert pat_data == {"sub-pt1": {time1: raw1}}

    # adding second file to db
    misc_path = op.join(
        mne.datasets.misc.data_path(), 'seeg', 'sample_seeg_ieeg.fif')
    raw2 = mne.io.read_raw(misc_path, preload=True)
    databasing(misc_path)
    time2 = '10/18/2019, 11:09:44'
    pat_data["sub-1"][time2].load_data()
    assert pat_data == {"sub-pt1": {time1: raw1}, "sub-1": {time2: raw2}}


"""
@pytest.mark.parametrize("dictionary, keyy, val, out", [
    (patient_statuses, "cool", 2, {"cool": [2]}),
    (patient_statuses, "fun", 6, {"cool": [2], "fun": [6]}),
    (patient_statuses, "fun", 8, {"cool": [2], "fun": [6, 8]})
])
def test_add_element(dictionary, keyy, val, out):
    from dev.eeg_final import add_element
    add_element(dictionary, keyy, val)
    assert patient_statuses == out
"""


def test_log_pat():
    from dev.eeg_final import logging_patient
    with LogCapture() as log_c:
        logging_patient({"patient_id": 1})
        log_c.check(("root", "INFO", "New patient registered under patient"
                                     " id {'patient_id': 1}"))


def test_log_info():
    from dev.eeg_final import logging_inf
    with LogCapture() as log_c:
        logging_inf({"attending_username": "Bud",
                     "attending_email": "cool@guy.com"})
        log_c.check(("root", "WARNING",
                     "New patient information"
                     " registered:  {'attending_username': 'Bud', "
                     "'attending_email': 'cool@guy.com'}"))


def test_log_email():
    from dev.eeg_final import logging_email
    with LogCapture() as log_c:
        logging_email(1, "nice", "cool@guy.com")
        log_c.check((
            "root", "INFO", 'Patient Needing Help: patient id 1,'
                            ' status info nice, to nurse or doctor at '
                            'email cool@guy.com'))

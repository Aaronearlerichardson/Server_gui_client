import json
import os
import pytest
import tkinter as tk

test_file = os.path.join("test_data", "test_data1.csv")
with open(os.path.join("tests", "b64.txt"), "r") as fobj:
    txt = fobj.read()

# TODO: fix gui testing and add create output test


def test_im_to_b64():
    from GUI_client import image_to_b64
    answer = image_to_b64(os.path.join("tests", "image.png"))
    assert answer == txt


def test_data_to_fig():
    from GUI_client import data_to_fig, preprocess_data
    data = preprocess_data(test_file)
    data_to_fig(data, "temp.png")
    assert os.path.isfile("temp.png")
    os.remove("temp.png")


def test_photometrics():
    root = tk.Tk()  # create dummy window for linux tests
    from GUI_client import photometrics_from_csv
    ans_photo_data, ans_metrics = photometrics_from_csv(test_file)
    for key, value in ans_metrics.items():
        if isinstance(value, tuple):
            ans_metrics[key] = list(value)
    with open(os.path.join("tests", "test_data1.json"), "r") as jobj:
        expected_metrics = json.load(jobj)
    expected_metrics["filename"] = os.path.basename(test_file)
    ans_photo = tk.PhotoImage(data=ans_photo_data)
    expected_photo = tk.PhotoImage(file=os.path.join("tests", "image.png"))
    assert isinstance(ans_photo, tk.PhotoImage)
    assert (ans_photo.width(), ans_photo.height()) == (
        expected_photo.width(), expected_photo.height())
    assert ans_metrics == expected_metrics
    assert not os.path.isfile("temp.png")


@pytest.mark.parametrize("pid, name, image, hr, expected", [
    ("201", "", "", "", {"patient_id": "201"}),
    ("", "", "", "", False),
    ("", "Ann", "image", "72", False),
    ("201", "Ann", "image", "72", {"patient_id": "201", "patient_name": "Ann",
                                   "image": ["image"], "hr": "72"})
])
def test_create_out(pid, name, image, hr, expected):
    from GUI_client import create_output
    answer = create_output(pid, name, image, hr)
    assert answer == expected


def test_html_search():
    from server import render_image, app
    from GUI_client import img_from_html
    with app.app_context():
        my_html = render_image(txt, "Ann")
    answer = img_from_html(my_html)
    assert answer == txt
    bad_answer = img_from_html("")
    assert bad_answer == ""

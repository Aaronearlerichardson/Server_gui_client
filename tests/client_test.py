import os
import json
from PIL import Image, ImageTk

test_file = os.path.join("test_data", "test_data1.csv")
with open(os.path.join("tests", "image.jpg"), "rb") as fobj:
    img = fobj.read()

# TODO: fix gui testing and add create output test


def test_im_to_b64():
    from GUI_client import image_to_b64
    with open(os.path.join("tests", "b64.txt"), "r") as fobj:
        expected = fobj.read()
    answer = image_to_b64(os.path.join("tests", "image.jpg"))
    assert answer == expected


def test_data_to_fig():
    from GUI_client import data_to_fig, preprocess_data
    data = preprocess_data(test_file)
    data_to_fig(data, "temp.jpg")
    assert os.path.isfile("temp.jpg")
    os.remove("temp.jpg")


def test_photometrics():
    from GUI_client import photometrics_from_csv
    ans_photo, ans_metrics = photometrics_from_csv(test_file)
    for key, value in ans_metrics.items():
        if isinstance(value, tuple):
            ans_metrics[key] = list(value)
    with open(os.path.join("tests", "test_data1.json"), "r") as jobj:
        expected_metrics = json.load(jobj)
    expected_metrics["filename"] = os.path.basename(test_file)
    image = Image.open(os.path.join("tests", "image.jpg"))
    expected_photo = ImageTk.PhotoImage(image=image)
    assert isinstance(ans_photo, ImageTk.PhotoImage)
    assert (ans_photo.width(), ans_photo.height()) == (
        expected_photo.width(), expected_photo.height())
    assert ans_metrics == expected_metrics
    assert not os.path.isfile("temp.jpg")

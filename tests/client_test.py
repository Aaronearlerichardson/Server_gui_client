import os

with open(os.path.join("tests", "image.jpg"), "rb") as fobj:
    img = fobj.read()


def test_im_to_b64():
    from GUI_client import image_to_b64
    with open(os.path.join("tests", "b64.txt"), "r") as fobj:
        expected = fobj.read()
    answer = image_to_b64(os.path.join("tests", "image.jpg"))
    assert answer == expected


def test_data_to_fig():
    from GUI_client import data_to_fig
    data_to_fig(os.path.join("test_data", "test_data1.csv"), "temp.jpg")
    assert os.path.isfile("temp.jpg")
    os.remove("temp.jpg")

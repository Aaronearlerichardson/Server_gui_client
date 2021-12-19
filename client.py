import requests
import os
from ecg_reader import preprocess_data
from calculations import get_metrics
import base64
import matplotlib.pyplot as plt
from typing import TypeVar
from pandas import DataFrame

server = "http://127.0.0.1:5000"
PathLike = TypeVar("PathLike", str, bytes, os.PathLike)


def image_to_b64(img_obj: plt.Figure, img_file: PathLike = "temp.jpg") -> str:
    img_obj.savefig(img_file)
    with open(img_file, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding="utf-8")
    os.remove(img_file)
    return b64_string


def data_to_fig(data: DataFrame) -> plt.Figure:
    plt.ioff()
    fig = plt.figure()
    plt.plot(data["time"], data["voltage"])
    return fig


if __name__ == "__main__":
    folder = "test_data"
    filename = os.path.join(folder, "test_data1.csv")
    pre_data = preprocess_data(filename, raw_max=300, l_freq=1, h_freq=50,
                               phase="zero-double", fir_window="hann",
                               fir_design="firwin")
    figure = data_to_fig(pre_data)
    b64_str = image_to_b64(figure)
    metrics = get_metrics(pre_data, rounding=4)
    patient1 = {"patient_name": "Ann Ables",
                "patient_id": 201,
                "hr": metrics["mean_hr_bpm"],
                "image": b64_str}
    r = requests.post(server + "/new_patient", json=patient1)
    print(r.status_code)
    print(r.text)

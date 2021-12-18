import requests
import os
from ecg_reader import preprocess_data
from calculations import get_metrics
import base64


server = "http://127.0.0.1:5000"


def image_to_b64(filename: str) -> str:
    with open(filename, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding="utf-8")
    return b64_string


if __name__ == "__main__":
    folder = "test_data"
    filename = os.path.join(folder, "test_data1.csv")
    pre_data = preprocess_data(filename, raw_max=300, l_freq=1, h_freq=50,
                               phase="zero-double", fir_window="hann",
                               fir_design="firwin")
    metrics = get_metrics(pre_data, rounding=4)
    patient1 = {"name": "Ann Ables", "id": 201, "hr": metrics["mean_hr_bpm"]}
    patient1["image"] =
    r = requests.post(server + "/new_patient", json=patient1)
    print(r.status_code)
    print(r.text)

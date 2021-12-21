import requests
import os

from ecg_reader import preprocess_data
from calculations import get_metrics
import base64
import matplotlib.pyplot as plt
from typing import TypeVar, Tuple
from tkinter import ttk, filedialog
import tkinter as tk
from pandas import DataFrame
import json
import re

server = "http://127.0.0.1:5000"
PathLike = TypeVar("PathLike", str, bytes, os.PathLike)
i_file = "temp.png"


def image_to_b64(img_file: PathLike = "temp.jpg") -> str:
    with open(img_file, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding="utf-8")
    return b64_string


def data_to_fig(data: DataFrame, img_file: PathLike = "temp.jpg"):
    plt.ioff()
    plt.plot(data["time"], data["voltage"])
    plt.savefig(img_file)
    plt.close()


def photometrics_from_csv(file_name: PathLike) -> Tuple[str, dict]:
    assert file_name.endswith(".csv")
    data = preprocess_data(file_name, raw_max=300, l_freq=1, h_freq=50,
                           phase="zero-double", fir_window="hann",
                           fir_design="firwin")
    data_to_fig(data, i_file)
    b64_img = image_to_b64(i_file)
    metrics = get_metrics(data, rounding=4)
    os.remove(i_file)
    return b64_img, metrics


def create_output(patient_id: str,
                  patient_name: str = None,
                  image: str = None,
                  hr: str = None) -> dict:
    my_vars = locals()
    output = dict()
    for key, value in my_vars.items():
        if value:
            if key == "image":
                output[key] = [value]
            else:
                output[key] = value
    return output


def design_window():
    def send_button_cmd():
        name = name_data.get()
        my_id = id_data.get()
        b64_img = img_str.get()
        hr = heart_rate.get()

        if my_id:
            # call external fnx to do work that can be tested
            patient = create_output(my_id, name, b64_img, hr)
            # send data to the server
            r = requests.post(server + "/new_patient", json=patient)
            response_dict = json.loads(r.text)
            response_dict.pop("image")
            print_to_gui(response_dict)
        else:
            print_to_gui("patient ID is a required field")

    def cancel_cmd():
        root.destroy()

    def browse_files():
        file_name = filedialog.askopenfilename(
            initialdir=csv_file.get(), title="Select a File", filetypes=(
                ("csv files", "*.csv*"), ("all files", "*.*")))
        csv_file.set(file_name)
        b64_img, metrics = photometrics_from_csv(file_name)
        img_str.set(b64_img)
        heart_rate.set(str(metrics["mean_hr_bpm"]))
        photo = tk.PhotoImage(data=b64_img)
        img_grid.config(image=photo)
        img_grid.image_ref = photo  # keep as a reference
        img_label.config(text="Heart Rate: {} (bpm)".format(heart_rate.get()))

    def print_to_gui(msg: str):
        msg_label.config(text=msg)

    def query_files():
        r = requests.get(server + "/get")
        cache = list()
        response_dict = json.loads(r.text)
        for row in response_dict.values():
            cache.append(row["patient_id"])
        combo_box['values'] = cache

    def retrieve_file():
        r = requests.get(server + "/get/{}/image".format(patient_mrn.get()))
        img = re.search('data:image/png;base64,([^\']+)', r.text).group(1)
        photo = tk.PhotoImage(data=img)
        img_grid.config(image=photo)
        img_grid.image_ref = photo  # keep as a reference
        dat = requests.get(server + "/get/{}".format(patient_mrn.get()))
        data = json.loads(dat.text)
        heart_rate.set(data["hr"])
        img_label.config(text="Heart Rate: {} (bpm)".format(heart_rate.get()))
        id_data.set(data["patient_id"])
        name_data.set(data["patient_name"])

    root = tk.Tk()
    root.title("Health Database GUI")

    top_label = ttk.Label(root, text="ECG Database")
    top_label.grid(column=3, row=0, columnspan=1)

    ttk.Label(root, text="Name").grid(column=0, row=1, sticky="e")
    name_data = tk.StringVar()
    name_entry_box = ttk.Entry(root, width=30, textvariable=name_data)
    name_entry_box.grid(column=1, row=1, columnspan=2, sticky="w")

    ttk.Label(root, text="ID").grid(column=0, row=2)
    id_data = tk.StringVar()
    id_entry_box = ttk.Entry(root, width=10, textvariable=id_data)
    id_entry_box.grid(column=1, row=2, columnspan=2, sticky="w")

    ttk.Label(root, text="Local File").grid(column=4, row=1, sticky="e")
    csv_file = tk.StringVar()
    csv_file.set(os.getcwd())
    id_entry_box = ttk.Entry(root, width=23, textvariable=csv_file)
    id_entry_box.grid(column=5, row=1)

    ttk.Label(root, text="Server File").grid(column=4, row=2, sticky="e")
    patient_mrn = tk.StringVar()
    combo_box = ttk.Combobox(root, textvariable=patient_mrn,
                             postcommand=query_files)
    combo_box.grid(column=5, row=2)

    send_button = ttk.Button(root, text="Send", command=send_button_cmd)
    send_button.grid(column=1, row=6)

    cancel_button = ttk.Button(root, text="Cancel", command=cancel_cmd)
    cancel_button.grid(column=5, row=6)

    browse_button = ttk.Button(root, text="Browse", command=browse_files)
    browse_button.grid(column=6, row=1)

    retr_button = ttk.Button(root, text="Retrieve", command=retrieve_file)
    retr_button.grid(column=6, row=2)

    img_str = tk.StringVar()
    img_grid = tk.Label(root, image=tk.PhotoImage(data=img_str.get()))
    img_grid.grid(column=1, row=4, columnspan=6)

    heart_rate = tk.StringVar()
    img_label = ttk.Label(root, text="")
    img_label.grid(column=3, row=3, columnspan=2)

    msg_label = ttk.Label(root, text="")
    msg_label.grid(column=3, row=6, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    design_window()

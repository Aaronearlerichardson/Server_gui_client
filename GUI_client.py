import requests
import os

from PIL.ImageTk import PhotoImage

from ecg_reader import preprocess_data
from calculations import get_metrics
import base64
import matplotlib.pyplot as plt
from typing import TypeVar, Tuple
from tkinter import ttk, filedialog
import tkinter as tk
from PIL import Image, ImageTk
from pandas import DataFrame
from typing import Tuple

server = "http://127.0.0.1:5000"
PathLike = TypeVar("PathLike", str, bytes, os.PathLike)


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


def photometrics_from_csv(file_name: PathLike) -> Tuple[PhotoImage, dict]:
    assert file_name.endswith(".csv")
    data = preprocess_data(file_name, raw_max=300, l_freq=1, h_freq=50,
                           phase="zero-double", fir_window="hann",
                           fir_design="firwin")
    i_file = "temp.jpg"
    data_to_fig(data, i_file)
    metrics = get_metrics(data)
    image = Image.open(i_file)
    photo = ImageTk.PhotoImage(image)
    os.remove(i_file)
    return photo, metrics


def design_window():
    def ok_button_cmd():
        name = name_data.get()
        my_id = id_data.get()
        blood_letter = blood_letter_data.get()
        rh_factor = rh_data.get()

        # call external fnx to do work that can be tested
        answer = create_output(name, my_id, blood_letter, rh_factor)
        print(answer)

    def cancel_cmd():
        root.destroy()

    def browse_files():
        # TODO: modularize for testing
        file_name = filedialog.askopenfilename(
            initialdir=csv_file.get(), title="Select a File", filetypes=(
                ("csv files", "*.csv*"), ("all files", "*.*")))
        csv_file.set(file_name)
        photo, metrics = photometrics_from_csv(file_name)
        img_grid.config(image=photo)
        img_grid.image = photo  # keep as a reference
        img_label.config(text="Heart Rate: {} (bpm)".format(
            metrics["mean_hr_bpm"]))
        img_label.metrics = metrics

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

    ttk.Label(root, text="Data File").grid(column=4, row=1, sticky="e")
    csv_file = tk.StringVar()
    csv_file.set(os.getcwd())
    id_entry_box = ttk.Entry(root, width=23, textvariable=csv_file)
    id_entry_box.grid(column=5, row=1)

    ok_button = ttk.Button(root, text="Ok", command=ok_button_cmd)
    ok_button.grid(column=1, row=6)

    cancel_button = ttk.Button(root, text="Cancel", command=cancel_cmd)
    cancel_button.grid(column=2, row=6)

    browse_button = ttk.Button(root, text="Browse", command=browse_files)
    browse_button.grid(column=6, row=1)
    img_grid = tk.Label(root, image=tk.PhotoImage(data=""))
    img_grid.grid(column=1, row=4, columnspan=6)

    img_label = ttk.Label(root, text="")
    img_label.grid(column=3, row=3, columnspan=2)

    root.mainloop()


def main(filename: PathLike):
    pre_data = preprocess_data(filename, raw_max=300, l_freq=1, h_freq=50,
                               phase="zero-double", fir_window="hann",
                               fir_design="firwin")

    img_file = "temp.jpg"
    data_to_fig(pre_data)
    b64_str = image_to_b64(img_file)
    os.remove(img_file)

    metrics = get_metrics(pre_data, rounding=4)
    patient1 = {"patient_name": "Ann Ables",
                "patient_id": 201,
                "hr": metrics["mean_hr_bpm"],
                "image": [b64_str]}
    r = requests.post(server + "/new_patient", json=patient1)
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    design_window()

import requests
import os
from ecg_reader import preprocess_data
from calculations import get_metrics
import base64
import matplotlib.pyplot as plt
from typing import TypeVar
from pandas import DataFrame
from tkinter import ttk
import tkinter as tk

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


def create_output(name, id, blood_letter, rh_factor):
    out_string = "Patient name: {}\n".format(name)

    out_string += "Blood type: {}{}\n".format(blood_letter, rh_factor)

    return out_string


def design_window():
    def ok_button_cmd():
        name = name_data.get()

        id = id_data.get()

        blood_letter = blood_letter_data.get()

        rh_factor = rh_data.get()

        # call external fnx to do work that can be tested

        answer = create_output(name, id, blood_letter, rh_factor)

        print(answer)

    def cancel_cmd():
        root.destroy()

    root = tk.Tk()

    root.title("Health Database GUI")

    top_label = ttk.Label(root, text="Blood Donor Database")

    top_label.grid(column=0, row=0, columnspan=2)

    ttk.Label(root, text="Name").grid(column=0, row=1, sticky="e")

    name_data = tk.StringVar()

    name_entry_box = ttk.Entry(root, width=50, textvariable=name_data)

    name_entry_box.grid(column=1, row=1, columnspan=2, sticky="w")

    ttk.Label(root, text="ID").grid(column=0, row=2)

    id_data = tk.StringVar()

    id_entry_box = ttk.Entry(root, width=10, textvariable=id_data)

    id_entry_box.grid(column=1, row=2, columnspan=2, sticky="w")

    blood_letter_data = tk.StringVar()
    blood_letter_data.set('AB')
    ttk.Radiobutton(root, text="A", variable=blood_letter_data,

                    value="A").grid(column=0, row=3, sticky=tk.W)

    ttk.Radiobutton(root, text="B", variable=blood_letter_data,

                    value="B").grid(column=0, row=4, sticky=tk.W)

    ttk.Radiobutton(root, text="AB", variable=blood_letter_data,

                    value="AB").grid(column=0, row=5, sticky=tk.W)

    ttk.Radiobutton(root, text="O", variable=blood_letter_data,

                    value="O").grid(column=0, row=6, sticky=tk.W)

    rh_data = tk.StringVar()
    rh_data.set('-')
    rh_checkbox = ttk.Checkbutton(root, text="Rh Positive",
                                  variable=rh_data, onvalue="+", offvalue="-")

    rh_checkbox.grid(column=1, row=4)

    ttk.Label(root, text="Nearest Donation Center").grid(column=3, row=0)

    donation_center_data = tk.StringVar()
    combo_box = ttk.Combobox(root, textvariable=donation_center_data)
    combo_box.grid(column=3, row=1)

    ok_button = ttk.Button(root, text="Ok", command=ok_button_cmd)

    ok_button.grid(column=1, row=6)

    cancel_button = ttk.Button(root, text="Cancel", command=cancel_cmd)

    cancel_button.grid(column=2, row=6)

    root.mainloop()


if __name__ == "__main__":  # TODO: make the main shorter or put in a function
    design_window()
    folder = "test_data"
    filename = os.path.join(folder, "test_data1.csv")
    pre_data = preprocess_data(filename, raw_max=300, l_freq=1, h_freq=50,
                               phase="zero-double", fir_window="hann",
                               fir_design="firwin")

    img_file = "temp.jpg"
    data_to_fig(pre_data, img_file)
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

import base64
import json
import os
import tkinter as tk
from tkinter import ttk, filedialog
from typing import TypeVar, Tuple, Union

import requests
from matplotlib.figure import Figure
from pandas import DataFrame

from ecg_analysis.calculations import get_metrics
from ecg_analysis.ecg_reader import preprocess_data
from server import db

server = "http://vcm-23126.vm.duke.edu:5000"
PathLike = TypeVar("PathLike", str, bytes, os.PathLike)
i_file = "temp.png"


def image_to_b64(img_file: PathLike = "temp.png") -> str:
    """function that converts an image file to a base64 encoded string

    This function takes a file path to an image (default value 'temp.png') and
    converts that image to a base 64 encoded string. The encoding protocol of
    the string is utf-8. The file object is read as bytes into the string.

    :param img_file: Path to the image file, default value is 'temp.png'
    :type img_file: Pathlike
    :return: Base 64 string of the image file
    :rtype: str
    """
    with open(img_file, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding="utf-8")
    return b64_string


def data_to_fig(data: DataFrame, img_file: PathLike = "temp.png"):
    """function that saves a matplotlib figure from a two column DataFrame

    This function takes a Pandas Dataframe with the columns 'time' and
    'voltage' as well as the name of the image file to write the plot to. It
    takes this data and saves the figure to the indicated image file. It favors
    usage of the matplotlib figure object over pyplot due to issues with
    backend and tkinter when using pyplot.

    source: https://stackoverflow.com/questions/37604289

    :param data: DataFrame with columns "time" and "voltage"
    :type data: DataFrame
    :param img_file: Path string for intended file to write the figure image to
    :type img_file: Pathlike
    """
    fig = Figure()
    ax = fig.subplots()
    ax.plot(data["time"], data["voltage"])
    fig.savefig(img_file)


def photometrics_from_csv(file_name: PathLike) -> Tuple[str, dict]:
    """Takes a csv ecg file and converts it to a b64 string and heart metrics

    This function takes a csv file with two columns and preprocesses that file,
    assigning those columns to either the 'time' or 'voltage' column in a
    DataFrame. That DataFrame is then converted to matplotlib figure which is
    converted to a b64 string image and a series of relevant metrics for ECGs.
    The figure conversion step creates a temporary 'temp.png' file which the
    img_to_b64 function uses to generate the b64 string. After this is
    accomplished, the temporary file is deleted.

    :param file_name: The file path of the csv data file to be preprocessed
    :type file_name: Pathlike
    :return: The b64 image and relevant heart rhythm metrics
    :rtype: Tuple[str, dict]
    """
    assert file_name.endswith(".csv")
    data = preprocess_data(file_name, raw_max=300, l_freq=1, h_freq=50,
                           phase="zero-double", fir_window="hann",
                           fir_design="firwin")
    data_to_fig(data, i_file)
    b64_img = image_to_b64(i_file)
    metrics = get_metrics(data, rounding=4)
    os.remove(i_file)
    return b64_img, metrics


def img_from_html(html_str: str) -> str:
    """Scrubs the string of a html page for the b64 string of in image

    This function uses regex to scan the html template described in the render
    image function. It scans this template for the base 64 string encoded png
    image and extracts it from the template. This string is then returned.

    :param html_str: The string of the html page to be searched
    :type html_str: str
    :return: The Base 64 string of the png image
    :rtype: str
    """
    from re import search
    match_obj = search('data:image/png;base64,([^\']+)', html_str)
    if match_obj:
        match = match_obj.group(1)
        return match
    else:
        return ""


def create_output(patient_id: str,
                  patient_name: str,
                  image: str,
                  hr: str) -> Union[dict, bool]:
    """Takes the inputs and converts it to a POST request format

    This function takes the patient_id, patient_name, image, and heart rate
    (hr) and inserts them into a dictionary to be sent in a POST request to the
    server. All inputs are required, but because the inputs are tkinter
    StringVars, any 'missing' inputs will be read in as empty strings. If the
    parameter indicated to be the index is an empty string, this function
    returns False. Any other parameter that is an empty string will just not be
    added to the POST request. If the parameter 'image' is not empty, that is
    inserted into a list before it is added to the dictionary.

    :param patient_id: The MRN of the patient
    :type patient_id: str
    :param patient_name: The name of the patient
    :type patient_name: str
    :param image: The patient's ECG image, encoded as a base 64 string
    :type image: str
    :param hr: The calculated average heart rate of the patient, calculated
        from the ECG image
    :type hr: str
    :return: A POST request compatible dictionary with keys matching the
        parameter names
    :rtype: dict
    """
    my_vars = locals()
    if my_vars[db.Index] == "":
        return False
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

        # call external fnx to do work that can be tested
        patient = create_output(my_id, name, b64_img, hr)
        if patient is False:
            print_to_gui("patient ID is a required field")
        else:
            # send data to the server
            r = requests.post(server + "/new_patient", json=patient)
            response_dict = json.loads(r.text)
            if "image" in response_dict.keys():
                response_dict.pop("image")
            print_to_gui(response_dict)

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
        if patient_mrn.get() == "":
            print_to_gui("Patient MRN is required")
            return
        dat = requests.get(server + "/get/{}".format(patient_mrn.get()))
        data = json.loads(dat.text)
        id_data.set(data["patient_id"])
        if "patient_name" in data.keys():
            name_data.set(data["patient_name"])
        else:
            name_data.set("")
        if "hr" in data.keys():
            heart_rate.set(data["hr"])
            img_label.config(
                text="Heart Rate: {} (bpm)".format(heart_rate.get()))
            r = requests.get(
                server + "/get/{}/image".format(patient_mrn.get()))
            img = img_from_html(r.text)
            img_str.set(img)
            photo = tk.PhotoImage(data=img)
            img_grid.config(image=photo)
            img_grid.image_ref = photo  # keep as a reference
        else:
            img_grid.image_ref = tk.PhotoImage(data="")
            img_str.set("")
            heart_rate.set("")
            img_label.config(text="")

    root = tk.Tk()
    root.title("Health Database GUI")

    top_label = ttk.Label(root, text="ECG Database")
    top_label.grid(column=3, row=0, columnspan=2)

    ttk.Label(root, text="Name").grid(column=0, row=1, sticky="e")
    name_data = tk.StringVar()
    name_entry_box = ttk.Entry(root, width=30, textvariable=name_data)
    name_entry_box.grid(column=1, row=1, columnspan=2, sticky="w")

    ttk.Label(root, text="ID").grid(column=0, row=2, sticky="e")
    id_data = tk.StringVar()
    id_entry_box = ttk.Entry(root, width=30, textvariable=id_data)
    id_entry_box.grid(column=1, row=2, columnspan=2, sticky="w")

    ttk.Label(root, text="Local File").grid(column=4, row=1, sticky="e")
    csv_file = tk.StringVar()
    csv_file.set(os.getcwd())
    file_entry_box = ttk.Entry(root, width=23, textvariable=csv_file)
    file_entry_box.grid(column=5, row=1, sticky="w")

    ttk.Label(root, text="Server File").grid(column=4, row=2, sticky="e")
    patient_mrn = tk.StringVar()
    combo_box = ttk.Combobox(root, textvariable=patient_mrn,
                             postcommand=query_files)
    combo_box.grid(column=5, row=2, sticky="w")

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
    img_grid.grid(column=1, row=4, columnspan=5)

    heart_rate = tk.StringVar()
    img_label = ttk.Label(root, text="")
    img_label.grid(column=3, row=3, columnspan=2)

    msg_label = ttk.Label(root, text="")
    msg_label.grid(column=3, row=6, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    design_window()

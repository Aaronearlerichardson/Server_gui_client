import tkinter as tk
import logging
from tkinter import Variable, ttk, Button, Entry
from flask import Flask, request
import requests
app = Flask(__name__)


@app.route("/annotations", methods=["POST"])
def take_notes():
    """App route post that gets patient data and
    runs design window.

    This fnx requests patient data and runs patient id
    through the design window for the nurse gui to work.

    :param: N/A

    :returns: design window gui for writing info and 200 code
    """
    my_id = request.get_data()
    stat = design_window(my_id)
    return stat, 200


def create_output(my_id, status):
    out_string = "Patient ID: {}\n".format(my_id)
    out_string += "Patient Info: {}\n".format(status)
    return out_string


def design_window(id1):
    def ok_button_cmd(id2):
        status = status_data.get()
        out_string = create_output(id2, status)
        print(out_string)
        output_string.configure(text=out_string)

    def cancel_cmd():
        root.destroy()

    root = tk.Tk()
    root.title("Patient Status to Nurse Station GUI")
    top_label = ttk.Label(root, text=id1)
    top_label.grid(column=0, row=0, columnspan=2, sticky="w")
    ttk.Label(root, text="ID").grid(column=0, row=1, sticky="e")
    status_data = tk.StringVar()
    id_entry_box = ttk.Entry(root, width=40, textvariable=status_data)
    id_entry_box.grid(column=1, row=1, sticky="w", columnspan=2)

    output_string = ttk.Label(root)
    output_string.grid()

    ok_button = ttk.Button(root, text="Ok", command=lambda: ok_button_cmd(
        id1))
    ok_button.grid(column=1, row=6)

    cancel_button = ttk.Button(root, text="Cancel", command=cancel_cmd)
    cancel_button.grid(column=2, row=6)

    root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(filename="Information.log", filemode="w",
                        level=logging.INFO)
    app.run(host="0.0.0.0", port=6000)

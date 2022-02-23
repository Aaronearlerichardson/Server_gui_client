import mne
import logging
from flask import Flask, request
import requests
app = Flask(__name__)
pat_data = {}
patient_statuses = {}


@app.route("/", methods=["GET"])
def get_status():  # no test needed!
    """Applies route for showing that the server is on.

    This route fnx is a get request that when the address
    http://vcm-23126.vm.duke.edu/ is inputted online, returns a
    jsonified string that says "Server is on".

    :param: N/A

    :returns: json string that the server is on
    """
    return "Server is on"


@app.route("/database", methods=["POST"])
def add_data():  # no test needed!
    """Fnx requests files, saves them, extracts necessary elements,
    and uses a post request to add patient written information to
    a preestablished dictionary.

    This route fnx is a post request that checks the file type and
    determines its correctness for further code use, requests the file
    and saves it, then uses databasing to extract certain dictionary elements
    and send an email when there is a problem. The requets acesses the other
    server nurse gui and inputs the written data from nurse notes for the
    respective patient. This is appended to the pre made dictionary of
    dictionaries for the patient and the request is returned.
    jsonified string that says "Server is on".

    :param: N/A

    :returns: dictionary of sent email information
    """
    infofile = validate_file_input(request.files)
    if infofile[0] is not True:
        return infofile
    file = request.files["raw_ieeg.fif"]

    file.save(file.filename)
    email = databasing(file.filename)
    patient1 = email["subject"]
    email["gui_resp"] = requests.post("http://" +
        request.remote_addr + ":6000/annotations", data=patient1).text
    add_element(patient_statuses, patient1, email["gui_resp"])
    logging_patient(patient1)
    logging_inf(patient_statuses)
    print(patient_statuses)
    return email, 200


def add_element(dict, key, value):
    """This function adds elements to a dictionary if
     the key is not already present.

    This fnx takes in a dictionary, key string, and value
    data. Using an if statement it checks if the key is
    present and if not, it appends the given value data
    to that key within the dictionory.

    :param dict:dictionary of information
    :param key:string denoting key of dict
    :param value: data to be stored in key

    :returns: inputted dictionary with added key and
    accompanying data (if key not present)
    """
    if key not in dict:
        dict[key] = []
    dict[key].append(value)


def databasing(file):
    """Extracts patient data and sends email

    This fnx takes in raw fif file and extracts patient info
    as well as adding time of patient scanning. These are added to
    a patient dictionary with accompanying values. The function
    emailing is called which sends a pseudo email to alert the
    doctor or nurse (depending on choice) of a issue.

    :param file: fif file with raw object eeg data

    :returns: dictionary of data that was sent in pseudo
    email
    """
    raw = mne.io.read_raw_fif(file)
    sub_id = raw.info["subject_info"]["his_id"]
    scan_time = raw.info["meas_date"].strftime("%m/%d/%Y, %H:%M:%S")
    pat_data[sub_id] = {}
    pat_data[sub_id][scan_time] = raw
    sent = emailing(sub_id, "nurse/dockool@gmail.com", pat_data, scan_time)
    return sent


def validate_file_input(file: dict):
    """This fnx checks if file is correct type for code

    This fnx tales in a file and if it is not the one
    needed it returns an error and if it is it returns
    true.

    :param file:dictionary file

    :returns: str and error code or boolean and error code
    """
    if not file:
        return "The input was not a correct file type", 400
    return True, 200


def emailing(my_id: str, email: str, status: str, time: str):  # no test!
    """Sends a pseudo email to attending if the patient is found
    to be in trouble.

    The emailing fnx uses an inline route post
    method to send an email with information on the patient and
    that they need help. The dictionary it outputs contains
    from email, to email, and content (id, status, and time/date).
    It uses the inputs my_id, email, status, and time
    in order to populate these "email" sections.

    :param my_id: str value of patient id
    :param email: str of attending email
    :param status: str patient info
    :param time: time that patient in need (str)

    :returns: from and to email if patient needs help; blank
    str and 200 code if not. Logs to file that email was sent.
    """
    out = {"from_email": "salma.moncayoreyes@duke.edu", "to_email": email,
           "subject": "Patient {} needs assistance".format(my_id),
           "content": "ID: {}, Status: {},"
                      " Time/Date: {}!".format(my_id, status, time)}
    r = requests.post("http://vcm-7631.vm.duke.edu:5007/hrss/send_email",
                      json=out)
    print(r.text)
    logging_email(my_id, status, email)
    return out


def logging_patient(pat1):
    """Logs when a new patient is added
    
    This function takes in a dictionary of the new patient
    addition then uses logging info and puts in the patient id
    value into the log string using the patient_id key

    :param pat1: dictionary containing new patient information

    :returns: info log string containing the patient id
    """
    logging.info("New patient registered under"
                 " patient id {}".format(pat1))


def logging_inf(pat_stat):
    """Logs when a new patient info is added

    This function takes in a dictionary of the new patient
    addition then uses logging info and puts in the patient id
    value into the log string using the patient_id key

    :param pat_stat: dictionary containing new patient information

    :returns: info log string containing the patient info dictionary
    """
    logging.warning("New patient information registered: "
                    " {}".format(pat_stat))


def logging_email(my_id, status, email):
    """Logs when a patient needs help

    This function takes in id interger value, status,
    and the desired email related. Then it logs this in a
    string onto a log file.

    :param my_id: interger value of patient id
    :param status: str value of patient info
    :param email: str of email

    :returns: info log string containing the patient id,status, and email
    """
    logging.info("Patient Needing Help: patient id {}, status info {},"
                 " to nurse or doctor at"
                 " email {}".format(my_id, status, email))


if __name__ == '__main__':
    logging.basicConfig(filename="Information.log", filemode="w",
                        level=logging.INFO)
    app.run(host="0.0.0.0", port=5000)

from datetime import datetime
from typing import Union, Dict, Tuple, TypedDict

from flask import Flask, request, render_template_string

from database import Database
from ecg_analysis.ecg_reader import is_num

app = Flask(__name__)
db_keys = {"patient_id": int, "patient_name": str, "hr": float, "image": list}
db = Database(index="patient_id")
t_format = "%m-%d-%Y %H:%M:%S"
db_entry = TypedDict("db_entry", **db_keys)


@app.route("/", methods=["GET"])
def get_status():  # no test needed!
    """Applies route for showing that the server is on.

    This route function is a get request that when the address
    http://vcm-23126.vm.duke.edu/ is inputted online, returns a
    jsonified string that says "Server is on".

    :return: json string that the server is on
    :rtype: Tuple[str, int]
    """
    return "Server is on", 200


@app.route("/new_patient", methods=["POST"])
def new_patient():
    """This applies the new_patient route to post new patient information to a
    dictionary.

    This function is a POST request that when the address
    http://vcm-23126.vm.duke.edu/new_patient is inputted online, returns a
    jsonified string that states a dictionary of the patient_id, the
    patient_name, the heart rate as 'hr', and the time that the data was stored
    in the database. This function uses the posted dictionary of new patient
    data and checks the id and hr calling the correct input function, which
    uses try intify and try floatify as backend. Then, the function calls the
    validate input function that checks if the input was a dictionary(if not,
    return string and 400 error), if the key specified is missing(if missing
    return string and 400 error), and if the data type of each key is correct
    (if not return str and 400). If all of this is correct, returns True and
    200 code. Once the data is determined to be True, then the time is recorded
    and it is added to a database and the added data as a ditionary is returned
    stating that a new patient was added with the code 200.


    :return: dictionary that includes patient_id, patient_name, time,
    and hr; string + error code or string + completion code
    :rtype: Tuple[dict, int]
    """
    data = request.get_json()
    data = correct_input(data, db_keys)
    if not isinstance(data, dict):
        return data, 400
    error_msg, status_code = validate_input(data, db_keys)
    if status_code != 200:
        return error_msg, status_code
    data: db_entry
    added = db.add_entry(data, time=datetime.now().strftime(t_format))
    return added, 200


@app.route("/get", methods=["GET"])
def get_all():
    """Applies route for showing all data present on the server

    This function is a GET request that when the address
    http://vcm-23126.vm.duke.edu/get is inputted online, returns a
    jsonified string that states all the data contained in the database defined
    in database.py. The jsonified string, when parsed, is a dictionary with MRN
    numbers as keys and all data associated with those MRNs as values. If the
    database is empty, returns an empty dict.


    :return: Dictionary with mrns as keys and data as values
    :rtype: Tuple[dict, int]
    """
    all_dict = dict()
    if "patient_id" in db.__dict__.keys():
        for mrn in db.patient_id:
            all_dict[mrn] = db.search(patient_id=mrn)
    return all_dict, 200


@app.route("/get/<name_or_mrn>", methods=["GET"])
def get_data(name_or_mrn: str) -> Tuple[Union[dict, str], int]:
    """Applies route for showing all data associated with name or mrn

    This function is a GET request that when the address
    http://vcm-23126.vm.duke.edu/get/<name_or_mrn> is inputted online, returns
    a jsonified string that states all the data contained in the database
    associated with the name or MRN inputted. If there is more than one MRN
    associated with the name given, then the most recent mrn is returned, and
    other data can only be retrieved by inputting the mrn of the older data.

    :param name_or_mrn: name or mrn of the relevant data to be retrieved
    :type name_or_mrn: str
    :return: data associated with that name or mrn
    :rtype: Tuple[dict, int]
    """
    try:
        mrn = try_intify(name_or_mrn)
        match = db.search(patient_id=mrn, patient_name=name_or_mrn)
        if "image" in match.keys():
            del match["image"]
        return match, 200
    except IndexError as e:
        return str(e), 405


@app.route("/get/<name_or_mrn>/image", methods=["GET"])
def get_image(name_or_mrn: str) -> Tuple[str, int]:
    """Applies route for showing image associated with the given name or mrn

    This function is a GET request that when the address
    http://vcm-23126.vm.duke.edu/get/<name_or_mrn>/image is inputted online,
    returns a html rendered string (using render_image) that shows the image
    and associated name on a webpage associated with the name or MRN inputted.
    If there is more than one MRN associated with the name given, then the most
    recent mrn is returned, and other images can only be retrieved by inputting
    the mrn of the older data.

    :param name_or_mrn: name or mrn of the relevant data to be retrieved
    :type name_or_mrn: str
    :return: html string of rendered image and name
    :rtype: Tuple[str, int]
    """
    try:
        mrn = try_intify(name_or_mrn)
        data = db.search(patient_id=mrn, patient_name=name_or_mrn)
    except IndexError as e:
        return str(e), 405
    if "image" not in data.keys():
        return "No image was uploaded for ID {}".format(
            data["patient_id"]), 405
    b64_img = data["image"][-1]
    if "patient_name" in data.keys():
        name = data["patient_name"]
    else:
        name = ""
    page = render_image(b64_img, name)
    return page, 200


def render_image(b64_img: str, name: str) -> str:
    """Converts b64 image and patient name to a rendered html page

    This function takes a b64 png image and patient name and converts it to a
    string which can be rendered in a standard html page on a browser. It does
    this by inserting the data into a locally stored html template and
    returning a correctly rendered image and name on a webpage.

    :param b64_img: A string that is a base64 encoded image that decodes into
        image bytes
    :type b64_img: str
    :param name: The name of the patient
    :type name: str
    :return: A rendered html string that encodes for a webpage
    :rtype: str
    """
    template_string = """<h1>{{ my_title }}<h1>
    <img src='data:image/png;base64,{{ img_data }}'
        alt='img_data'  id='imgslot'/>"""
    page = render_template_string(template_string,
                                  my_title=name,
                                  img_data=b64_img)
    return page


def try_intify(num: Union[int, float, bool, str, complex]) -> Union[int, bool]:
    """Tries to convert input to integer and if this is not possible,
    then the func returns false.

    The func runs the value through a series of statements that
    determine if the value has an imaginary value of 0 (return only the
    real integer value or otherwise to return False), if the value
    is a float and if it is equal to the integer of that value
    (returns the integer), if the value is a boolean (returns False),
    or if there is any other error to return False.

    :param num: single value can be int, float, bool, str, complex
    :type num: Union[int, float, bool, str, complex]
    :return: integer if it was convertable and a False if not
    :rtype: Union[int, bool]
    """
    if isinstance(num, complex):  # TESTED
        if num.imag == 0:
            num = num.real
        else:
            return False
    elif isinstance(num, bool):
        return False
    try:
        if int(num) == float(num):
            return int(num)
        else:
            return False
    except ValueError:
        return False


def try_floatify(num: Union[int, float, bool, str, complex]
                 ) -> Union[float, bool]:
    """Function that tests if object can be converted to number

    A function that takes any input and detects if it is a number by
    attempting to convert the input to a float. This function catches
    convertable digit string cases.

    Source:
    https://stackoverflow.com/questions/354038

    :param num: object data to determine if it is conceivably a number
    :type num: Union[int, float, bool, str, complex]
    :return: a boolean determination if the input is a number, or the floating
        point number itself
    :rtype: Union[float, bool]
    """

    if is_num(num):
        if isinstance(num, complex):
            num = num.real
        return float(num)
    else:
        return False


def validate_input(in_data: dict,  # TESTED
                   expected: Dict[str, type]) -> Tuple[Union[str, bool], int]:
    """Determines if the data given is a dictionary, if the key exsists in
    the input, and if the value in the key matches the type that was expected.

    An expectation of the type of data in each key is established
    and fed into this function along with a dictionary data set.
    The Validate input funx then checks if the input was a dictionary(if not,
    return string and 400 error), if the key specified is missing(if missing
    return string and 400 error), and if the data type of each key is correct
    (if not return str and 400).

    :param in_data: dictionary of data
    :param expected: dictionary data key types expectations (tuple)

    :return: String and 400 error (not dictionary, or wrong dictionary value
     type) or True + 200 code.
    :rtype: Tuple[Union[str, bool], int]

    """
    if not isinstance(in_data, dict):
        return "The input was not a dictionary.", 400
    for key, value in expected.items():
        if key not in in_data.keys():
            continue
        elif not isinstance(in_data[key], value):
            return "the key '{}' is a {}, should be {}".format(
                key, type(in_data[key]), expected[key]), 400
    return True, 200


def correct_input(in_data: Dict[str, Union[str, list]],
                  expected: Dict[str, type]) -> Union[db_entry, str]:
    """Convert the default string inputs of the GUI into the indicated types

    Takes the dictionary in_data from the post request and converts the values
    to the data types indicated in the expected type dictionary. If the
    conversion fails, the function returns a string indicating where the error
    occurred. The internal conversions are handled by try_intify and
    try_floatify for int and float types respectively.

    :param in_data: Data received to the server by the POST request
    :type in_data: Dict[str, Union[str, list]]
    :param expected: Typed dictionary with keys matching the in_data keys
    :type expected: Dict[str, type]
    :return: A dictionary with correspondingly corrected types such that the
        types match the expected types
    :rtype: Union[db_entry, str]
    """
    out_data = dict()
    for key, val in in_data.items():
        if expected[key] is int:
            i = try_intify(val)
            if i is False:
                return "key {} is not convertable to an integer".format(key)
            else:
                out_data[key] = i
        elif expected[key] is float:
            i = try_floatify(val)
            if i is False:
                return "key {} is not convertable to a float".format(key)
            else:
                out_data[key] = i
        else:
            out_data[key] = val
    return out_data


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

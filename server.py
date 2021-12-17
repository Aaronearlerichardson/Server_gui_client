from flask import Flask, request
from pandas import DataFrame

app = Flask(__name__)
db = DataFrame()

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


@app.route("/new_patient", methods=["POST"])
def new_patient():  # no test needed!
    """This applies the new_patient route to post
    new patient information to a dictionary.

    This function is a POST request that when the address
    http://vcm-23126.vm.duke.edu/api/new_patient is inputted online, returns a
    jsonified string that states a dictionary of the patient_id, the
    attending_username, and the patient_age. This function uses the posted
    dictionary of new patient data and checks the id and age calling the try
    intify function. Try intify runs the key values through a series of
    statements that determine if it has an imaginary value of 0 (return the
    real interger value or otherwise to return False), if the value is a float
    and if it is equal to the interger of that value (returns the interger), if
    the value is a boolean (returns False), or if there is any other error
    to return False. Then this function runs a loop to output a
    string that tells the user if the values are not convertible to
    intergers. Then, the function calls validate input funx that checks
    if the input was a dictionary(if not, return string and 400 error), if
    the key specified is missing(if missing return string and 400 error),
    and if the data type of each key is correct (if not return str and 400).
    If all of this is correct, returns True and 200 code. Once the data is
    determined to be True, it is added to a database and a string is returned
    stating that a new patient was added with the code 200.


    :param: N/A

    :returns: list of dictionary that includes patient_id, attending_username,
    and patient_age; string + error code or string + completion code
    """
    data = request.get_json()
    data["patient_id"] = try_intify(data["patient_id"])
    data["patient_age"] = try_intify(data["patient_age"])
    for key, i in data.items():
        if i is False:
            return "key {} is not convertable to an integer".format(key), 400
    expected_keys = {"patient_id": int, "attending_username": str,
                     "patient_age": int}
    error_str, status_code = validate_input(data, expected_keys)
    if error_str is not True:
        return error_str, status_code

    return "Added patient {}".format(added), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
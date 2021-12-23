import json
import logging
import os

from neurokit2 import ecg_peaks
from pandas import DataFrame

import ecg_analysis.ecg_reader as erd


def get_metrics(data: DataFrame,
                t_key: str = "time",
                v_key: str = "voltage",
                rounding: int = 3) -> dict:
    """Calculates all relevant metrics in an ECG data set

    This function takes in a dataframe with the keys 't_key' and 'v_key' which
    by default are 'time' and 'voltage' respectively. It returns a dictionary
    with the duration, voltage extremes, filename, number of beats, beats per
    minute, anda list of beat times stored in it paired with the relevant key.
    Each numeric metric is rounded to three decimal places by default, which
    can be changed by assigning an integer to the 'rounding' parameter

    :param data: A pandas dataframe that contains the fields t_key and v_key
    :type data: DataFrame
    :param t_key: String indicating the name of the time column in data.
        'time' by default.
    :type t_key: str
    :param v_key: String indicating the name of the voltage column in data.
        'voltage' by default.
    :type v_key: str
    :param rounding: An integer indicating the number of decimals to round to.
        3 by default
    :type rounding: int
    :return: A dictionary with the keys: duration, beats, extremes, filename,
        num_beats, mean_hr_bpm
    :rtype: dict
    """
    metrics = dict(filename=data.name)
    logging.info("For file: " + data.name)

    metrics["duration"] = round(data[t_key].iloc[-1] - data[t_key].iloc[0],
                                rounding)
    logging.info("The duration was {}".format(metrics["duration"]))

    metrics["extremes"] = (round(data[v_key].max(), rounding),
                           round(data[v_key].min(), rounding))
    logging.info("The {} extremes were {}".format(v_key, metrics["extremes"]))

    _, peak_dict = ecg_peaks(data[v_key], len(data)/metrics["duration"])
    metrics["beats"] = data[t_key].iloc[peak_dict["ECG_R_Peaks"]].to_list()
    beats_str = [str(i) for i in metrics["beats"]]
    logging.info("The beat times were [" + ", ".join(beats_str) + "]")

    metrics["num_beats"] = len(metrics["beats"])
    logging.info("The number of beats was {}".format(metrics["num_beats"]))

    metrics["mean_hr_bpm"] = round(metrics["num_beats"] / metrics["duration"]
                                   * 60, rounding)
    logging.info("The mean heart rate was {} bpm".format(metrics["mean_hr_bpm"]
                                                         ))
    return metrics


def dict2json(my_dict: dict, folder: str = "files"):
    """Takes a dict and folder name and writes dict data to file in folder

    Take a dictionary and writes it to a JSON file in a folder. Folder is
    called 'files' unless specified otherwise. The base name of the file is
    indicated by the 'filename' key in the dictionary, which is not included
    in the JSON itself

    :param my_dict: dictionary of items to write to the JSON file
    :type my_dict: dict
    :param folder: folder to save the files in. Default is 'files'
    :type folder: str
    """
    if not os.path.isdir(folder):
        os.mkdir(folder)
    filename = my_dict.pop("filename").strip(".csv") + ".json"
    full_file = os.path.join(folder, filename)
    with open(full_file, 'w') as fobj:
        json.dump(my_dict, fobj)


def remove_dir(directory: str):
    """Takes a folder name and removes it, even if it contains files

    Deletes the selected folder by listing through the files and deleting them
    one by one and then deleting the empty folder

    :param directory: Directory path to remove it and its contents
    :type directory: str
    """
    for file in os.listdir(directory):
        os.remove(os.path.join(directory, file))
    os.rmdir(directory)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # set logging parameters
    if os.path.isfile("info.log"):
        os.remove("info.log")
    logging.basicConfig(filename="info.log", level=logging.INFO, filemode="a")
    erd.set_log_file("info.log", overwrite=False,  # set log output for mne
                     output_format="%(levelname)s:%(name)s:%(message)s")

    # remove old data
    out_folder = "out_files"
    if os.path.isdir(out_folder):
        remove_dir(out_folder)

    # loop through data
    folder = "test_data"
    data = []
    for file in [i for i in os.listdir(folder) if i.endswith(".csv")]:
        fname = os.path.join(folder, file)
        if file == "test_data1_orig.csv":
            pre_data = erd.load_csv(fname, ["time", "voltage"]).astype(float)
            pre_data.name = fname
        else:
            pre_data = erd.preprocess_data(fname, raw_max=300, l_freq=1,
                                           h_freq=50, phase="zero-double",
                                           fir_window="hann",
                                           fir_design="firwin")
        metrics = get_metrics(pre_data, rounding=4)
        indexer = pre_data["time"].isin(metrics["beats"])
        if file in []:
            plt.plot(pre_data["time"], pre_data["voltage"],
                     pre_data["time"][indexer], pre_data["voltage"][indexer])
            plt.title(pre_data.name)
            plt.show()

        dict2json(metrics, out_folder)
        data.append(pre_data)

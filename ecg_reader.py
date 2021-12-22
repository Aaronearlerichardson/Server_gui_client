import logging
import os
from typing import Tuple, Union, List, Any

import numpy as np
from mne import filter, set_log_file
from pandas import DataFrame, Series, read_csv


def load_csv(local_file: str,
             cols: Union[List[str], Tuple[str]] = ("time", "voltage")
             ) -> DataFrame:
    """Loads a patient file.csv into a DataFrame

    Takes a file path to a csv file and reads then writes the data into a
    dataframe with the column headers indicated by cols.

    :param local_file: path to local .csv file
    :type local_file: str
    :param cols: list or tuple indicating the column headers for the output
        dataframe. ('time', 'voltage') by default
    :type cols: Union[List[str], Tuple[str]]
    :return: DataFrame read in of the csv file with headers given by cols
    :rtype: DataFrame
    :
    """

    assert os.path.isfile(local_file)
    if local_file.endswith(".csv"):
        new_data = read_csv(local_file, header=None, dtype=str,
                            na_filter=False)
        assert isinstance(new_data, DataFrame)
        if not len(new_data.columns) == len(cols):
            raise IndexError(
                "Please use correct number of column labels\n"
                "the given number of labels was {} and "
                "the required number was {}".format(
                    len(cols), len(new_data.columns)))
        new_data.columns = cols
        new_data.name = os.path.basename(local_file)
        return new_data
    else:
        logging.warning(file + " is not a csv file, and as such is not yet"
                               " supported in this module")


def is_num(num: Any) -> bool:
    """Function that tests if object can be converted to number

    A function that takes any input and detects if it is a number by
    attempting to convert the input to a float. This function catches
    convertable digit string cases.

    Source:
    https://stackoverflow.com/questions/354038

    :param num: object data to determine if it is conceivably an number
    :type num: Any
    :return: a boolean determination if the input is a number
    :rtype: bool
    """
    if isinstance(num, complex):
        if num.imag == 0:
            num = num.real
        else:
            return False
    elif isinstance(num, bool):
        return False
    try:
        float(num)
        return True
    except ValueError:
        return False


def apply_to_df(my_data: DataFrame, func: object, invert=False):
    """Applies given boolean function to DataFrame rows and removes False rows

    Takes a DataFrame my_data and applies a function func element by element to
    determine bool value. Per given row, it then checks if all column elements.
    If invert is False, then it deletes any rows where func is false in at
    least one column. Conversely, if invert is True, it deletes every row where
    func is true in at least one column.

    :param my_data: DataFrame where func is applied element-wise
    :type my_data: DataFrame
    :param func: function passed to apply. Takes in a DataFrame element and
        returns a boolean value
    :type func: object
    :param invert: Indication of whether to delete rows where the func is true
        or false in at least one column
    :type invert: bool
    :return: DataFrame where func returns true or false (depending on invert)
        for every column
    :rtype: DataFrame
    """
    assert callable(func)
    if invert:
        where_is = my_data.applymap(func).any(1)
        inds = my_data.index[np.where(where_is)[0]]
        new_data = my_data[~where_is]
    else:
        where_is = my_data.applymap(func).all(1)
        inds = my_data.index[np.where(~where_is)[0]]
        new_data = my_data[where_is]

    return new_data, inds


def is_nan(x: Union[int, float, str]) -> bool:
    """Check to see if x is an nan value

    Check to see if the given parameter x is an nan value. Similar to np.isnan,
    but with the capability to read strings as well as number types. Attempts
    to convert strings to floats to do so.

    :param x: Input to check if it is nan
    :type x: Union[int, float, str]
    :return: Boolean indicating the whether the input is nan
    :rtype: bool
    """
    try:
        y = float(x)
    except Exception:
        y = x

    if y != y:
        return True
    else:
        return False


def is_mt_str(my_str) -> bool:
    """Check to see if the given input is an empty string

    Function that checks the given parameter my_str to see if it is an empty
    string. Uses the innate identity __eq__ to check.

    :param my_str: String to check if it is empty
    :type my_str: str
    :return: Boolean indicating if the input is an empty string
    :rtype: bool
    """
    if not isinstance(my_str, str):
        return False
    elif "".__eq__(my_str):
        return True
    else:
        return False


def clean_data(my_data: DataFrame):
    """Cleans missing, nan, and non numeric values from a DataFrame

    Takes a DataFrame and checks each element for a missing, nan, or non
    numeric value and then removes the whole row if it does. Returns the
    cleaned DataFrame and logs the row indices and DataFrame names of
    erroneous rows.

    :param my_data: DataFrame to be cleaned
    :type my_data: DataFrame
    :return: DataFrame without any missing, nan, or non numeric values
    :rtype: DataFrame
    """
    big_len = len(my_data)
    num_data, empty_inds = apply_to_df(my_data.astype(str), is_mt_str,
                                       invert=True)
    num_data, no_num_inds = apply_to_df(num_data, is_num)
    cleaned_data, nan_inds = apply_to_df(num_data, is_nan, invert=True)
    for no_num_ind in no_num_inds:
        logging.error("removed non-numeric data from {} at "
                      "line {} out of {} data point"
                      "s".format(my_data.name, no_num_ind + 1, big_len))
    for nanline in nan_inds:
        logging.error("removed nan data from {} at "
                      "line {} out of {} data point"
                      "s".format(my_data.name, nanline + 1, big_len))
    for mtline in empty_inds:
        logging.error("removed missing data from {} at "
                      "line {} out of {} data point"
                      "s".format(my_data.name, mtline + 1, big_len))

    cleaned_data = cleaned_data.astype(float)
    cleaned_data.name = my_data.name
    return cleaned_data


def filter_data(my_data: Series, first_samp: Union[float, int],
                last_samp: Union[float, int], high: Union[float, int],
                low: Union[float, int], **kwargs) -> np.ndarray:
    """Filter ECG data using a band pass FIR filter with reflected padding

    Takes a pandas Series indicating voltage values of an ECG and filters it
    using a finite impulse response (FIR) filter. The padding is reflected to
    keep from too much attenuation or inversion of the signal. It uses the
    first and last time points to calculate the sample rate, and takes a
    variable high and low pass frequency for the band pass. This function uses
    mne for backend and their documentation can be found below. Keyword
    arguments corresponding to their documentation can be set in this function
    call.

    link: https://mne.tools/stable/generated/mne.filter.filter_data.html

    :param my_data: Series data describing the voltage time-series
    :type my_data: Series
    :param first_samp: number indicating the time at which the first sample was
        taken
    :type first_samp: Union[float, int]
    :param last_samp: number indicating the time at which the last sample was
        taken
    :type last_samp: Union[float, int]
    :param high: The top of the range of the band pass filter. Must be higher
        than the low parameter
    :type high: Union[float, int]
    :param low: The bottom of the range of the band pass filter. Must be lower
        than the high parameter
    :type low: Union[float, int]
    :return: numpy array of the filtered data
    :rtype: np.ndarray
    """
    assert isinstance(my_data, Series)
    numpy_data = my_data.to_numpy()
    sample_freq = len(my_data) / (last_samp - first_samp)
    shaped = np.reshape(numpy_data, (1, len(numpy_data)))
    cpus = os.cpu_count()
    if cpus is not None:
        kwargs["n_jobs"] = cpus
    filtered = filter.filter_data(shaped, sample_freq, low, high,
                                  verbose="info",
                                  pad="reflect",
                                  method="fir",
                                  **kwargs)
    filtered = filtered - np.mean(filtered) + np.mean(my_data)
    return filtered


def check_range(data_set: Series, filename: str,
                upper: Union[float, int],
                lower: Union[float, int]):
    """Checks to see if a value of a given Series is outside a given range

    Takes a Series and logs an error if there are any values above the param
    upper or below the param lower.

    :param data_set: Series to check the range of its values
    :type data_set: Series
    :param filename: File name to indicate in the error log
    :type filename: str
    :param upper: Upper limit of the range. Log if any values are above this.
    :type upper: Union[float, int]
    :param lower: Lower limit of the range. Log if any values are above this.
    :type lower: Union[float, int]
    """

    assert lower < upper
    inds = np.where(data_set > upper)[0].tolist() + np.where(
        data_set < lower)[0].tolist()
    inds.sort()
    for index in inds:
        if data_set.iloc[index] > upper:
            logging.error("data point {} in {} has a value higher"
                          " than {}".format(index, filename, upper))
            break
        elif data_set.iloc[index] < lower:
            logging.error("data point {} in {} has a value lower"
                          " than {}".format(index, filename, lower))
            break


def preprocess_data(file_path: str,
                    tlabel: str = "time",
                    vlabel: str = "voltage",
                    raw_max: Union[float, int] = 300,
                    raw_min: Union[float, int] = None,
                    l_freq: Union[float, int] = 1,
                    h_freq: Union[float, int] = 50,
                    clean_only: bool = False,
                    **kwargs) -> DataFrame:
    """ Takes a csv ECG file and runs a full preprocessing pipeline on it

    Reads a given csv file path into a DataFrame, which is assigned the headers
    tlabel and vlabel. First, it cleans any bad data from the DataFrae using
    clean_data(). It then logs whether an values are outside the range
    [raw_min, raw_max] and logs it. Lastly, it takes the vlabel column and
    filters it using the filter_data() function. Any mne keyword arguments may
    be piped into the filter function through **kwargs

    :param file_path: Path to the csv file the will be read into the DataFrame
    :type file_path: str
    :param tlabel: Label for the time column of the DataFrame.
    :type tlabel: str
    :param vlabel: Label for the voltage column of the DataFrame
    :type vlabel: str
    :param raw_max: Upper end of the range allowed for the voltage data.
    :type raw_max: Union[float, int]
    :param raw_min: Lower end of the range allowed for the voltage data.
        Default value is the negative of the raw_max.
    :type raw_min: Union[float, int]
    :param l_freq: Lower frequency band of the band pass filter
    :type l_freq: Union[float, int]
    :param h_freq: Upper frequency band of the band pas filter
    :type h_freq: Union[float, int]
    :param clean_only: Option to not filter the data
    :type clean_only: bool
    :return: A fully preprocessed DataFrame of the time and voltage data
    :rtype: DataFrame
    """
    # check inputs
    if raw_min is None:
        raw_min = raw_max * -1
    assert raw_min < raw_max
    assert l_freq < h_freq  # band pass filter, not a notch
    assert l_freq > 0

    raw = load_csv(file_path, [tlabel, vlabel])
    cleaned = clean_data(raw)
    pre_data = cleaned
    pre_data.name = cleaned.name
    check_range(cleaned[vlabel], raw.name, raw_max, raw_min)
    if clean_only:
        return cleaned
    voltage_filtered = filter_data(cleaned[vlabel],
                                   cleaned[tlabel].iloc[0],
                                   cleaned[tlabel].iloc[-1],
                                   h_freq,
                                   l_freq,
                                   **kwargs)
    pre_data[vlabel] = np.reshape(voltage_filtered,
                                  (voltage_filtered.shape[1]))
    pre_data.reset_index(drop=True, inplace=True)
    return pre_data


if __name__ == "__main__":

    # set logging parameters
    if os.path.isfile("info.log"):
        os.remove("info.log")
    logging.basicConfig(filename="info.log", level=logging.INFO, filemode="a")
    set_log_file("info.log", overwrite=False,  # set log output for mne
                 output_format="%(levelname)s:%(name)s:%(message)s")

    # loop through data
    pre_data = []
    folder = "test_data"
    for file in [i for i in os.listdir(folder) if i.endswith(".csv")]:
        filename = os.path.join(folder, file)
        pre_data.append(preprocess_data(filename,
                                        raw_max=300,
                                        l_freq=1,
                                        h_freq=50))

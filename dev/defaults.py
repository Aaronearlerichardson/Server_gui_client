""" A script that details the default values for many functions and tests"""

import mne
import bids
from mne_bids import BIDSPath, read_raw_bids


def layout(kwargs: dict = None) -> dict:
    """ The default key word arguments for the BIDSLayout data structure

    The BIDSLayout data structure is an integral part of the pybids workflow.
    Users need to be able to use the functionalities without needing to fill
    out unnecessary data in the inputs

    extension: the default extension is the brainvision binary and vhdr fil
    extension
    suffix: the default data type for this repo is ieeg
    scope: the default scope is the raw data group, as opposed to processed

    """
    if kwargs is None:
        kwargs = {}
    if "extension" not in kwargs.keys():  # change later to search
        kwargs["extension"] = "vhdr"
    if "suffix" not in kwargs.keys():
        kwargs["suffix"] = "ieeg"
    if "scope" not in kwargs.keys():
        kwargs["scope"] = "raw"
    return kwargs


class DefaultData(object):
    def __init__(self):
        """A class for all bids and ieeg data type defaults from mne-bids

        Testing intercranial eeg programs requires a set of very robust data to
        run the program on. This class provides easy access to that data
        provided by mne
        """
        super(DefaultData, self).__init__()
        self.root = mne.datasets.epilepsy_ecog.data_path()
        self.layout = bids.BIDSLayout(self.root)
        self.file = self.layout.get(**layout())[0]
        self.file: bids.layout.BIDSFile
        self.entities = self.file.get_entities()
        self.path = BIDSPath(root=self.root, **self.entities)
        self.raw = read_raw_bids(bids_path=self.path, verbose=False)
        self.raw.load_data()

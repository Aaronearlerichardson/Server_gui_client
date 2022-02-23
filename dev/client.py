import os
from typing import Dict, TypeVar, List
import mne
from mne.io.fiff.raw import read_raw_fif
import requests
import defaults
from bids import BIDSLayout
from bids.layout import BIDSFile
from mne_bids import BIDSPath, read_raw_bids
from pathlib import Path
from openneuro import download

PathLike = TypeVar("PathLike", str, bytes, os.PathLike)
server = "http://vcm-23126.vm.duke.edu:"


def download_data(dataset: str, subjects: List[str],
                  bids_root: PathLike = None) -> BIDSLayout:
    if bids_root is None:
        if "Downloads" in os.listdir(Path.home()):
            bids_root = os.path.join(Path.home(), "Downloads", "bids")
        elif "downloads" in os.listdir(Path.home()):
            bids_root = os.path.join(Path.home(), "downloads", "bids")
        else:
            bids_root = os.path.join(Path.home(), "bids")
    download(dataset=dataset, target_dir=bids_root,
             include=[f'sub-{subject}' for subject in subjects])
    layout = BIDSLayout(root=bids_root)
    return layout


def bids_to_raw(bids_file: BIDSFile) -> mne.io.BaseRaw:
    entities = bids_file.get_entities()
    root = bids_file.path.split("sub-" + entities["subject"])[0]
    bids_path = BIDSPath(root=root, **entities)
    raw = read_raw_bids(bids_path=bids_path)
    raw.load_data()
    return raw


def layout_to_raw_dict(layout: BIDSLayout, **kwargs) -> \
        Dict[str, Dict[int, mne.io.BaseRaw]]:
    kwargs = defaults.layout(kwargs)
    sub_ids = layout.get_subjects()
    runs = layout.get_runs()
    data = {}
    for sub_id in sub_ids:
        data[sub_id] = {}
        if len(runs) == 0:
            runs = [1]
        for run in runs:
            if layout.get_runs():
                kwargs["run"] = run
            BIDSFiles = layout.get(subject=sub_id, **kwargs)
            if len(BIDSFiles) != 1:
                raise IndexError("only one run and session can match search"
                                 " terms")
            raw = bids_to_raw(BIDSFiles[0])
            data[sub_id][run] = raw
    return data


def send_raw(raw_obj: mne.io.BaseRaw, serv_address: str) -> str:
    # filename = r"{}".format(
    #    os.path.splitext(os.path.basename(raw_obj.filenames[0]))[0] + ".fif")
    filename = 'raw_ieeg.fif'
    raw_obj.save(filename, overwrite=True)
    with open(r'raw_ieeg.fif', 'rb') as filedata:
        r = requests.post(serv_address, files={filename: filedata})

    os.remove(filename)
    return r.text


if __name__ == "__main__":
    misc_path = mne.datasets.misc.data_path()
    raw = mne.io.read_raw(os.path.join(
        misc_path, 'seeg', 'sample_seeg_ieeg.fif'))
    df = raw.to_data_frame()
    r = send_raw(raw, server + "5000/database")
    print(r)

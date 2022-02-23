# This Python file uses the following encoding: utf-8
import os.path as op
import matplotlib.pyplot as plt
import mne
import mne.viz as vfig
import nibabel as nib
import numpy as np
from PyQt5 import Qt
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QVBoxLayout,
                             QListView, QApplication, QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mne._freesurfer import _check_subject_dir
from mne.gui._ieeg_locate_gui import (IntracranialElectrodeLocator,
                                      _CH_PLOT_SIZE, _make_slice_plot)
from mne.transforms import (apply_trans, _get_trans, invert_transform,
                            apply_volume_registration)
from mne.viz.backends.renderer import _get_renderer

app = QApplication.instance()
if app is None:
    app = QApplication(["Intracranial Electrode Locator"])


class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent, raw):
        """Class that inherits the matplotlib conversion to pyQT funcitonality

        This class takes a matplotlib figure and converts it's properties to
        mesh well with pyQT's libraries

        parent: the class that will be inherited by Canvas after it's
        initial __init__ raw: a raw object of eeg data
        """
        fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        fig = raw.plot(show=False)
        super().__init__(fig)
        self.setParent(parent)
        self.ax.plot()
        self.ax.grid()


class App(QWidget):
    def __init__(self, raw):
        """The class that inherits the Widget part of pyqt to maintain
        manoeuvrability of the plot

        This class inherits the QWidget class so it can be seamlessely
        integrated into the pyqt framework. It also calls the Canvas class
        """
        super().__init__()
        self.resize(1600, 800)

        chart = Canvas(self, raw)


class Locator(IntracranialElectrodeLocator):
    def __init__(self, raw, trans, aligned_ct, subject=None,
                 subjects_dir=None, groups=None, verbose=None):
        """GUI for locating intracranial electrodes. Inherited from MNE Class

        A class inherited from the MNE toolbox to locate and reconstruct
        intercraial anatomies and orientations. It recieves the raw object
        and creates a 3D gui with a 2d side scroller option.

        raw: an mne raw object variable. used in many different applications
        trans: Transformation matrix. Allows for electrodes to be
            transformed to common space
        aligned_ct: The CT scan fully aligned to the mri/electrode coordinate
            space
        subject: Name of the subject
        subjects_dir: directory of all of the subjects as a string
        groups: study group that a subject can be categorized as
        verbose: verbosity of code execution

        .. note:: Images will be displayed using orientation information
                  obtained from the image header. Images will be resampled to
                  dimensions [256, 256, 256] for display.
                """

        # initialize QMainWindow class
        super(IntracranialElectrodeLocator, self).__init__()
        vfig.use_browser_backend("matplotlib")

        if not raw.info.ch_names:
            raise ValueError('No channels found in `info` to locate')

        # store info for modification
        self._info = raw.info
        self._verbose = verbose

        # load imaging data
        self._subject_dir = _check_subject_dir(subject, subjects_dir)
        self._load_image_data(aligned_ct)

        self._ch_alpha = 0.5
        self._radius = int(_CH_PLOT_SIZE // 100)  # starting 1/200 of image
        # initialize channel data
        self._ch_index = 0
        # load data, apply trans
        self._head_mri_t = _get_trans(trans, 'head', 'mri')[0]
        self._mri_head_t = invert_transform(self._head_mri_t)
        # load channels, convert from m to mm
        self._chs = {name: apply_trans(self._head_mri_t, ch['loc'][:3]) * 1000
                     for name, ch in zip(raw.info.ch_names, raw.info['chs'])}
        self._ch_names = list(self._chs.keys())
        # set current position
        if np.isnan(self._chs[self._ch_names[self._ch_index]]).any():
            self._ras = np.array([0., 0., 0.])
        else:
            self._ras = self._chs[self._ch_names[self._ch_index]].copy()
        self._current_slice = apply_trans(
            self._ras_vox_t, self._ras).round().astype(int)
        self._group_channels(groups)

        # GUI design
        plt_grid = QGridLayout()
        plts = [_make_slice_plot(), _make_slice_plot(), _make_slice_plot()]
        self._figs = [plts[0][1], plts[1][1], plts[2][1]]
        # plt_grid.addWidget(plts[0][0], 0, 0)
        # plt_grid.addWidget(plts[1][0], 0, 1)
        # plt_grid.addWidget(plts[2][0], 1, 0)
        self._renderer = _get_renderer(
            name='IEEG Locator', size=(400, 400), bgcolor='w')

        # Channel selector
        self._ch_list = QListView()
        self._ch_list.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        self._ch_list.setMinimumWidth(100)
        self._set_ch_names()

        # Plots
        self._plot_images()

        # Menus
        button_hbox = self._get_button_bar()

        # Put everything together
        plot_ch_hbox = QHBoxLayout()
        plot_ch_hbox.addLayout(plt_grid)
        plot_ch_hbox.addWidget(self._ch_list)

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(button_hbox)
        main_vbox.addLayout(plot_ch_hbox)
        main_vbox.addWidget(self._renderer.plotter)

        central_widget = QWidget()
        central_widget.setLayout(main_vbox)
        self.setCentralWidget(central_widget)

        # ready for user
        self._ch_list.setFocus()  # always focus on list


if __name__ == "__main__":
    # file paths seeg
    misc_path = mne.datasets.misc.data_path()
    CT_orig = nib.load(op.join(misc_path, 'seeg', 'sample_seeg_CT.mgz'))
    T1 = nib.load(op.join(misc_path, 'seeg', 'sample_seeg', 'mri', 'T1.mgz'))

    # For 3D ieeg
    reg_affine = np.array([
        [0.99270756, -0.03243313, 0.11610254, -133.094156],
        [0.04374389, 0.99439665, -0.09623816, -97.58320673],
        [-0.11233068, 0.10061512, 0.98856381, -84.45551601],
        [0., 0., 0., 1.]])
    # The above matrix is a pre computed solution to the registraion command
    # below. this matrix is provided given the below command often takes
    # upward of 15 minutes to run reg_affine,
    # _ = mne.transforms.compute_volume_registration( CT_orig, T1,
    # pipeline='rigids')
    CT_aligned = apply_volume_registration(CT_orig, T1, reg_affine)
    my_raw = mne.io.read_raw(
        op.join(misc_path, 'seeg', 'sample_seeg_ieeg.fif'))
    subj_trans = mne.coreg.estimate_head_mri_t(
        'sample_seeg', op.join(misc_path, 'seeg'))
    gui = Locator(my_raw, subj_trans, CT_aligned,
                  subject='sample_seeg',
                  subjects_dir=op.join(misc_path, 'seeg'))
    gui.show()

    # for 2d ieeg
    App(my_raw).plot()

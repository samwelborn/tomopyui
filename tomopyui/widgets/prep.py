import copy
import datetime
import pathlib
from abc import ABC
from functools import partial

import dask.array as da
import numpy as np
from ipywidgets import *

from tomopyui.backend.io import Metadata_Prep, Projections_Child
from tomopyui.backend.util.padding import *
from tomopyui.widgets.imports import ShiftsUploader
from tomopyui.widgets.view import (
    BqImViewer_Projections_Child,
    BqImViewer_Projections_Parent,
)

if os.environ["cuda_enabled"] == "True":
    from ..gpu.prep.alignment import shift_prj_cp, batch_cross_correlation
    from ..gpu.prep.sampling import shrink_and_pad_projections

from tomopyui.widgets.styles import header_font_style, button_font_style


from tomopyui.widgets.styles import header_font_style, button_font_style


import tomopy.misc.corr as tomocorr


class Prep(ABC):
    def __init__(self, Import):
        self.init_attributes(Import)
        self.init_widgets()
        self.set_observes()
        self.make_tab()

    def init_attributes(self, Import):

        self.Import = Import
        self.Import.Prep = self
        self.projections = Import.projections
        self.altered_projections = Projections_Child(self.projections)
        self.prep_list = []
        self.accordions_open = False
        self.preview_only = False
        self.tomocorr_median_filter_size = 3
        self.tomocorr_gaussian_filter_order = 0
        self.tomocorr_gaussian_filter_sigma = 3
        self.save_on = False
        self.metadata = Metadata_Prep()

    def init_widgets(self):
        """
        Initializes widgets in the Prep tab.
        """
        self.button_layout = Layout(width="45px", height="40px")

        # -- Main viewers --------------------------------------------------------------
        self.imported_viewer = BqImViewer_Projections_Parent()
        self.imported_viewer.create_app()
        self.altered_viewer = BqImViewer_Projections_Child(self.imported_viewer)
        self.altered_viewer.create_app()
        self.altered_viewer.ds_dropdown.options = [("Original", -1)]
        self.altered_viewer.ds_dropdown.value = -1

        # -- Headers for plotting -------------------------------------
        self.import_plot_header = "Imported Projections"
        self.import_plot_header = Label(
            self.import_plot_header, style=header_font_style
        )
        self.altered_plot_header = "Altered Projections"
        self.altered_plot_header = Label(
            self.altered_plot_header, style=header_font_style
        )

        # -- Header for methods -------------------------------------
        self.prep_list_header = "Methods"
        self.prep_list_header = Label(self.prep_list_header, style=header_font_style)

        # -- Prep List -------------------------------------
        self.prep_list_select = Select(
            options=["Method 1", "Method 2", "Method 3", "Method 4", "Method 5"],
            rows=10,
            disabled=True,
        )
        # -- Buttons for methods list -------------------------------------
        self.up_button = Button(
            disabled=True,
            icon="arrow-up",
            tooltip="Move method up.",
            layout=self.button_layout,
            style=button_font_style,
        )
        self.down_button = Button(
            disabled=True,
            icon="arrow-down",
            tooltip="Move method down.",
            layout=self.button_layout,
            style=button_font_style,
        )
        self.remove_method_button = Button(
            disabled=True,
            icon="fa-minus-square",
            tooltip="Remove selected method.",
            layout=self.button_layout,
            style=button_font_style,
        )
        self.start_button = Button(
            disabled=True,
            button_style="info",
            tooltip=(
                "Run the list above. "
                + "This will save a subdirectory with your processed images."
            ),
            icon="fa-running",
            layout=self.button_layout,
            style=button_font_style,
        )
        self.preview_only_button = Button(
            disabled=True,
            button_style="",
            tooltip=(
                "Run the currently selected image through your list of methods. "
                + "This will not run the stack or save data."
            ),
            icon="glasses",
            layout=self.button_layout,
            style=button_font_style,
        )
        self.save_on_button = Button(
            disabled=True,
            button_style="",
            tooltip=("Turn this on to save the data when you click the run button."),
            icon="fa-file-export",
            layout=self.button_layout,
            style=button_font_style,
        )
        self.methods_button_box = VBox(
            [
                HBox(
                    [
                        self.up_button,
                        self.down_button,
                        self.remove_method_button,
                    ]
                ),
                HBox(
                    [
                        self.preview_only_button,
                        self.start_button,
                        self.save_on_button,
                    ]
                ),
            ]
        )

        # -- Main Viewers -------------------------------------------------------------

        self.viewer_hbox = HBox(
            [
                VBox(
                    [
                        self.import_plot_header,
                        self.imported_viewer.app,
                    ],
                    layout=Layout(align_items="center"),
                ),
                VBox(
                    [
                        self.prep_list_header,
                        self.prep_list_select,
                        self.methods_button_box,
                    ],
                    layout=Layout(align_items="center", align_content="center"),
                ),
                VBox(
                    [
                        self.altered_plot_header,
                        self.altered_viewer.app,
                    ],
                    layout=Layout(align_items="center"),
                ),
            ],
            layout=Layout(justify_content="center", align_items="center"),
        )

        # -- Shifts uploader --------------------------------------------------------
        self.shifts_uploader = ShiftsUploader(self)
        self.shift_x_header = "Shift in X"
        self.shift_x_header = Label(self.shift_x_header, style=header_font_style)
        self.shifts_sx_select = Select(
            options=[],
            rows=10,
            disabled=True,
        )
        self.shift_y_header = "Shift in Y"
        self.shift_y_header = Label(self.shift_y_header, style=header_font_style)
        self.shifts_sy_select = Select(
            options=[],
            rows=10,
            disabled=True,
        )
        self.shifts_filechooser_label = "Filechooser"
        self.shifts_filechooser_label = Label(
            self.shifts_filechooser_label, style=header_font_style
        )

        # -- List manipulation ---------------------------------------------------------
        self.buttons_to_disable = [
            self.prep_list_select,
            self.start_button,
            self.up_button,
            self.down_button,
            self.remove_method_button,
            self.start_button,
            self.preview_only_button,
            self.save_on_button,
        ]

        # -- Add preprocessing steps widgets -------------------------------------------

        # tomopy.misc.corr Median Filter
        self.tomocorr_median_filter_button = Button(
            description="Median Filter",
            button_style="",
            tooltip="Add a median filter to your data.",
            icon="fa-filter",
            layout=Layout(width="auto"),
        )
        # tomopy.misc.corr Median Filter options
        self.tomocorr_median_filter_size_dd = Dropdown(
            description="Size",
            options=list((str(i), i) for i in range(1, 25, 2)),
            value=3,
        )

        self.tomocorr_median_filter_box = HBox(
            [
                self.tomocorr_median_filter_button,
                self.tomocorr_median_filter_size_dd,
            ]
        )
        # tomopy.misc.corr Gaussian Filter
        self.tomocorr_gaussian_filter_button = Button(
            description="Gaussian Filter",
            button_style="",
            tooltip="Add a gaussian filter to your data.",
            icon="fa-filter",
            layout=Layout(width="auto"),
        )
        # tomopy.misc.corr Gaussian Filter options
        self.tomocorr_gaussian_filter_sigma_tb = BoundedFloatText(
            description="σ (stdv)",
            value=3,
            min=0,
            max=25,
        )
        self.tomocorr_gaussian_filter_order_dd = Dropdown(
            description="Order",
            options=[("Zeroth", 0), ("First", 1), ("Second", 2), ("Third", 3)],
            value=0,
            min=0,
            max=25,
        )

        self.tomocorr_gaussian_filter_box = HBox(
            [
                self.tomocorr_gaussian_filter_button,
                self.tomocorr_gaussian_filter_sigma_tb,
                self.tomocorr_gaussian_filter_order_dd,
            ],
        )

        self.remove_data_outside_button = Button(
            description="Set data = 0 outside of current histogram range.",
            layout=Layout(width="auto", height="auto"),
        )
        self.remove_data_outside_button.on_click(self.remove_data_outside)

        self.renormalize_by_roi_button = Button(
            description="Click to normalize by ROI.",
            button_style="info",
            layout=Layout(width="auto", height="auto"),
            disabled=False,
        )
        self.renormalize_by_roi_button.on_click(self.add_ROI_background)

        self.roi_buttons_box = VBox(
            [self.remove_data_outside_button, self.renormalize_by_roi_button]
        )
        self.prep_buttons = [
            self.tomocorr_median_filter_box,
            self.tomocorr_gaussian_filter_box,
            self.roi_buttons_box,
        ]

    # -- Functions to add to list ----------------------------------------
    def add_shift(self, *args):
        method = PrepMethod(
            self,
            "Shift",
            shift_projections,
            [
                list(self.shifts_uploader.sx),
                list(self.shifts_uploader.sy),
            ],
        )
        self.prep_list.append(method.method_tuple)
        self.update_prep_list()

    def add_tomocorr_median_filter(self, *args):
        self.tomocorr_median_filter_size = self.tomocorr_median_filter_size_dd.value
        method = PrepMethod(
            self,
            "Median Filter",
            tomocorr.median_filter,
            [
                self.tomocorr_median_filter_size,
            ],
        )
        self.prep_list.append(method.method_tuple)
        self.update_prep_list()

    def add_tomocorr_gaussian_filter(self, *args):
        self.tomocorr_gaussian_filter_sigma = (
            self.tomocorr_gaussian_filter_sigma_tb.value
        )
        self.tomocorr_gaussian_filter_order = (
            self.tomocorr_gaussian_filter_order_dd.value
        )
        method = PrepMethod(
            self,
            "Gaussian Filter",
            tomocorr.gaussian_filter,
            [
                self.tomocorr_gaussian_filter_sigma,
                self.tomocorr_gaussian_filter_order,
            ],
        )
        self.prep_list.append(method.method_tuple)
        self.update_prep_list()

    def add_ROI_background(self, *args):
        method = PrepMethod(
            self,
            "ROI Normalization",
            renormalize_by_roi,
            [
                self.imported_viewer.px_range_x,
                self.imported_viewer.px_range_y,
            ],
        )
        self.prep_list.append(method.method_tuple)
        self.update_prep_list()

    def remove_data_outside(self, *args):
        method = PrepMethod(
            self,
            "Remove Data Outside",
            remove_data_outside,
            [(self.imported_viewer.hist.vmin, self.imported_viewer.hist.vmax)],
        )
        self.prep_list.append(method.method_tuple)
        self.update_prep_list()

    def update_prep_list(self):
        if self.prep_list == []:
            self.prep_list_select.options = [
                "Method 1",
                "Method 2",
                "Method 3",
                "Method 4",
                "Method 5",
            ]
            for x in self.buttons_to_disable:
                x.disabled = True
        else:
            self.prep_list_select.options = [x[0] for x in self.prep_list]
            for x in self.buttons_to_disable:
                x.disabled = False

    def refresh_plots(self):
        self.imported_viewer.plot(self.projections, no_check=True)
        self.altered_projections.parent_projections = self.projections
        self.altered_projections.copy_from_parent()
        self.altered_viewer.plot(self.projections, no_check=True)

    def set_observes(self):

        # Start button
        self.start_button.on_click(self.run_prep_list)

        # Shifts - find upload callback in Imports

        # tomopy.misc.corr Median Filter
        self.tomocorr_median_filter_button.on_click(self.add_tomocorr_median_filter)

        # tomopy.misc.corr Gaussian Filter
        self.tomocorr_gaussian_filter_button.on_click(self.add_tomocorr_gaussian_filter)

        # Remove method
        self.remove_method_button.on_click(self.remove_method)

        # Move method up
        self.up_button.on_click(self.move_method_up)

        # Move method down
        self.down_button.on_click(self.move_method_down)

        # Preview
        self.preview_only_button.on_click(self.preview_only_on_off)

        # Save
        self.save_on_button.on_click(self.save_on_off)

    def update_shifts_list(self):
        pass

    def save_on_off(self, *args):
        if self.save_on:
            self.save_on_button.button_style = ""
            self.save_on = False
        else:
            self.save_on_button.button_style = "success"
            self.save_on = True

    def preview_only_on_off(self, *args):
        if self.preview_only:
            self.preview_only_button.button_style = ""
            self.preview_only = False
        else:
            self.preview_only_button.button_style = "success"
            self.preview_only = True

    def remove_method(self, *args):
        ind = self.prep_list_select.index
        self.prep_list.pop(ind)
        self.update_prep_list()

    def move_method_up(self, *args):
        ind = self.prep_list_select.index
        if ind != 0:
            self.prep_list[ind], self.prep_list[ind - 1] = (
                self.prep_list[ind - 1],
                self.prep_list[ind],
            )
            self.update_prep_list()
            self.prep_list_select.index = ind - 1

    def move_method_down(self, *args):
        ind = self.prep_list_select.index
        if ind != len(self.prep_list) - 1:
            self.prep_list[ind], self.prep_list[ind + 1] = (
                self.prep_list[ind + 1],
                self.prep_list[ind],
            )
            self.update_prep_list()
            self.prep_list_select.index = ind + 1

    # -- Load metadata button ---------------------------------------------
    def _load_metadata_all_on_click(self, change):
        self.load_metadata_button.button_style = "info"
        self.load_metadata_button.icon = "fas fa-cog fa-spin fa-lg"
        self.load_metadata_button.description = "Importing metadata."
        self.load_metadata_button.button_style = "success"
        self.load_metadata_button.icon = "fa-check-square"
        self.load_metadata_button.description = "Finished importing metadata."

    # -- Button to start alignment ----------------------------------------
    def run_prep_list(self, change):
        change.button_style = "info"
        change.icon = "fas fa-cog fa-spin fa-lg"
        self.run()
        change.button_style = "success"
        change.icon = "fa-check-square"

    def run(self):
        if self.preview_only:
            image_index = self.imported_viewer.image_index_slider.value
            self.altered_viewer.image_index_slider.value = image_index
            self.prepped_data = copy.deepcopy(self.altered_viewer.plotted_image.image)
            self.prepped_data = self.prepped_data[np.newaxis, ...]
            for prep_method_tuple in self.prep_list:
                prep_method_tuple[1].update_method_and_run()
            self.altered_viewer.plotted_image.image = self.prepped_data
        else:
            self.altered_projections.parent_projections = (
                self.imported_viewer.projections
            )
            self.altered_projections.deepcopy_data_from_parent()
            self.prepped_data = self.altered_projections.data
            for num, prep_method_tuple in enumerate(self.prep_list):
                prep_method_tuple[1].update_method_and_run()
                self.prep_list_select.index = num
            self.altered_projections.data = self.prepped_data
            self.altered_viewer.images = self.altered_projections.data
            self.altered_viewer.plotted_image.image = self.altered_projections.data[0]
            if self.save_on:
                self.make_prep_dir()
                self.metadata.set_metadata(self)
                self.metadata.filedir = self.filedir
                self.metadata.save_metadata()
                self.altered_projections.data = da.from_array(
                    self.altered_projections.data
                )
                hist, r, bins, percentile = self.altered_projections._dask_hist()
                grp = self.altered_projections.hdf_key_norm + "/"
                data_dict = {
                    self.altered_projections.hdf_key_norm_proj: self.altered_projections.data,
                    grp + self.altered_projections.hdf_key_bin_frequency: hist[0],
                    grp + self.altered_projections.hdf_key_bin_edges: hist[1],
                    grp + self.altered_projections.hdf_key_image_range: r,
                    grp + self.altered_projections.hdf_key_percentile: percentile,
                }
                self.altered_projections.dask_data_to_h5(
                    data_dict, savedir=self.filedir
                )
                self.altered_projections._dask_bin_centers(
                    grp, write=True, savedir=self.filedir
                )

    def make_prep_dir(self):
        now = datetime.datetime.now()
        dt_string = now.strftime("%Y%m%d-%H%M%S-prep")
        self.filedir = pathlib.Path(self.Import.projections.filedir) / dt_string
        self.filedir.mkdir()
        # os.mkdir(self.filedir)

    def make_tab(self):

        # -- Box organization -------------------------------------------------

        self.top_of_box_hb = HBox(
            [self.Import.switch_data_buttons],
            layout=Layout(
                width="auto",
                justify_content="flex-start",
            ),
        )
        self.viewer_accordion = Accordion(
            children=[self.viewer_hbox],
            selected_index=None,
            titles=("Plot Projection Images",),
        )
        self.prep_buttons_hbox = VBox(
            self.prep_buttons,
            layout=Layout(justify_content="center"),
        )
        self.prep_buttons_accordion = Accordion(
            children=[self.prep_buttons_hbox],
            selected_index=None,
            titles=("Add Preprocessing Methods",),
        )

        self.shifts_box = HBox(
            [
                VBox(
                    [
                        widgets.Label("Quick path search:"),
                        self.shifts_uploader.quick_path_search,
                    ],
                ),
                VBox(
                    [
                        self.shifts_filechooser_label,
                        self.shifts_uploader.filechooser,
                    ],
                ),
                VBox(
                    [
                        self.shift_x_header,
                        self.shifts_sx_select,
                    ],
                ),
                VBox(
                    [
                        self.shift_y_header,
                        self.shifts_sy_select,
                    ],
                ),
                self.shifts_uploader.import_button.button,
            ],
            layout=Layout(justify_content="center"),
        )

        self.shifts_accordion = Accordion(
            children=[self.shifts_box],
            selected_index=None,
            titles=("Upload shifts from prior alignments",),
        )
        self.tab = VBox(
            children=[
                self.top_of_box_hb,
                self.viewer_accordion,
                self.prep_buttons_accordion,
                self.shifts_accordion,
            ]
        )


class PrepMethod:
    def __init__(self, Prep, method_name: str, func, opts: list):
        self.Prep = Prep
        self.method_name = method_name
        self.func = func
        self.opts = opts
        self.method_tuple = (self.method_name, self)

    def update_method_and_run(self):
        self.partial_func = partial(self.func, self.Prep.prepped_data, *self.opts)
        self.Prep.prepped_data = self.partial_func()


def shift_projections(projections, sx, sy):
    new_prj_imgs = copy.deepcopy(projections)
    pad_x = int(np.ceil(np.max(np.abs(sx))))
    pad_y = int(np.ceil(np.max(np.abs(sy))))
    pad = (pad_x, pad_y)
    new_prj_imgs = pad_projections(new_prj_imgs, pad)
    new_prj_imgs = shift_prj_cp(
        new_prj_imgs,
        sx,
        sy,
        5,
        pad,
        use_corr_prj_gpu=False,
    )
    return new_prj_imgs


def shift_projections_nopad(projections, sx, sy):
    new_prj_imgs = copy.deepcopy(projections)
    new_prj_imgs = shift_prj_cp(
        new_prj_imgs,
        sx,
        sy,
        5,
        (0, 0),
        use_corr_prj_gpu=False,
        use_pad_cond=False,
    )
    return new_prj_imgs


def renormalize_by_roi(projections, px_range_x, px_range_y):
    averages = [
        np.mean(
            projections[i, px_range_y[0] : px_range_y[1], px_range_x[0] : px_range_x[1]]
        )
        for i in range(len(projections))
    ]
    projections = [projections[i] / averages[i] for i in range(len(projections))]
    return projections


def remove_data_outside(projections, vmin_vmax: tuple):
    remove_high_indexes = projections > vmin_vmax[1]
    projections[remove_high_indexes] = 1e-6
    remove_low_indexes = projections < vmin_vmax[0]
    projections[remove_low_indexes] = 1e-6
    return projections


### May use?
# def rectangle_selector_on(self, change):
#     time.sleep(0.1)
#     if self.viewer.rectangle_selector_on:
#         self.renormalize_by_roi_button.disabled = False
#     else:
#         self.renormalize_by_roi_button.disabled = True

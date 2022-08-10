from tomopyui.widgets.view import BqImViewerBase
from ipywidgets import *
import bqplot as bq
from tomopyui._sharedvars import *


class BqImViewer_HDF5(BqImViewerBase):
    def __init__(self):

        super().__init__()
        self.rectangle_selector_button.tooltip = (
            "Turn on the rectangular region selector. Select a region "
            "and copy it over to Altered Projections."
        )
        self.from_hdf = True
        self.from_npy = False

    def create_app(self):
        self.button_box = HBox(
            self.init_buttons,
            layout=self.footer_layout,
        )

        footer2 = VBox(
            [
                self.button_box,
                HBox(
                    [
                        self.status_bar_xrange,
                        self.status_bar_yrange,
                        self.status_bar_intensity,
                    ],
                    layout=self.footer_layout,
                ),
                HBox(
                    [
                        self.status_bar_xdistance,
                        self.status_bar_ydistance,
                    ],
                    layout=self.footer_layout,
                ),
            ],
            layout=self.footer_layout,
        )
        footer = VBox([self.footer1, footer2])
        self.app = VBox([self.header, self.center, footer])

    def plot(self, projections, hdf_handler):
        self.projections = projections
        self.hdf_handler = hdf_handler
        self.filedir = self.projections.filedir
        self.px_size = self.projections.px_size
        self.hist.precomputed_hist = self.projections.hist
        self.original_images = self.projections.data
        if self.hdf_handler.loaded_ds:
            self.images = self.projections.data_ds
        else:
            self.images = self.projections.data
        self.set_state_on_plot()

    # Downsample the plot view
    def downsample_viewer(self, *args):
        if self.hdf_handler.turn_off_callbacks:
            return
        self.ds_factor = self.ds_dropdown.value
        if self.ds_factor != -1:
            self.hdf_handler.load_ds(str(self.ds_factor))
            self.original_images = self.projections.data
            self.images = self.projections.data_ds
            self.hist.precomputed_hist = self.projections.hist
        elif self.ds_factor == -1:
            self.hdf_handler.load_any()
            self.original_images = self.projections.data
            self.images = self.projections.data
            self.hist.precomputed_hist = self.projections.hist

        self.plotted_image.image = self.images[self.image_index_slider.value]
        self.change_aspect_ratio()

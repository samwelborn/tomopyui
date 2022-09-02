from tomopyui.widgets.imports.imports import ImportBase, UploaderBase
from tomopyui.widgets.view import BqImViewer_Projections_Parent
from tomopyui.backend.io import Metadata
from ipywidgets import *

class Import_ALS832(ImportBase):
    """"""

    def __init__(self):
        super().__init__()
        self.raw_uploader = RawUploader_ALS832(self)
        self.make_tab()

    def make_tab(self):

        self.switch_data_buttons = HBox(
            [self.use_raw_button.button, self.use_prenorm_button.button],
            layout=Layout(justify_content="center"),
        )

        # raw_import = HBox([item for sublist in raw_import for item in sublist])
        self.raw_accordion = Accordion(
            children=[
                VBox(
                    [
                        HBox(
                            [self.raw_uploader.metadata_table_output],
                            layout=Layout(justify_content="center"),
                        ),
                        HBox(
                            [self.raw_uploader.progress_output],
                            layout=Layout(justify_content="center"),
                        ),
                        self.raw_uploader.app,
                    ]
                ),
            ],
            selected_index=None,
            titles=("Import and Normalize Raw Data",),
        )

        self.prenorm_accordion = Accordion(
            children=[
                VBox(
                    [
                        HBox(
                            [self.prenorm_uploader.metadata_table_output],
                            layout=Layout(justify_content="center"),
                        ),
                        self.prenorm_uploader.app,
                    ]
                ),
            ],
            selected_index=None,
            titles=("Import Prenormalized Data",),
        )

        self.tab = VBox(
            [
                self.raw_accordion,
                self.prenorm_accordion,
            ]
        )



class RawUploader_ALS832(UploaderBase):
    """
    Raw uploaders are the way you get your raw data (projections, flats, dark fields)
    into TomoPyUI. It holds a ProjectionsBase subclass (see io.py) that will do all of
    the data import stuff. the ProjectionsBase subclass for SSRL is
    RawProjectionsXRM_SSRL62. For you, it could be named
    RawProjectionsHDF5_APSyourbeamlinenumber().

    """

    def __init__(self, Import):
        super().__init__()  # look at UploaderBase __init__()
        self._init_widgets()
        self.projections = RawProjectionsHDF5_ALS832()
        self.reset_metadata_to = Metadata_ALS_832_Raw
        self.Import = Import
        self.filechooser.title = "Import Raw hdf5 File"
        self.filetypes_to_look_for = [".h5"]
        self.files_not_found_str = "Choose a directory with an hdf5 file."

        # Creates the app that goes into the Import object
        self.create_app()

    def _init_widgets(self):
        """
        You can make your widgets more fancy with this function. See the example in
        RawUploader_SSRL62C.
        """
        pass

    def import_data(self):
        """
        This is what is called when you click the blue import button on the frontend.
        """
        with self.progress_output:
            self.progress_output.clear_output()
            display(self.import_status_label)
        tic = time.perf_counter()
        self.projections.import_file_all(self)
        toc = time.perf_counter()
        self.projections.metadatas = Metadata.get_metadata_hierarchy(
            self.projections.metadata.filedir / self.projections.metadata.filename
        )
        self.import_status_label.value = f"Import and normalization took {toc-tic:.0f}s"
        self.viewer.plot(self.projections)

    def update_filechooser_from_quicksearch(self, h5files):
        """
        This is what is called when you update the quick path search bar. Right now,
        this is very basic. If you want to see a more complex version of this you can
        look at the example in PrenormUploader.

        This is called after _update_filechooser_from_quicksearch in UploaderBase.
        """
        if len(h5files) == 1:
            self.filename = h5files[0]
        elif len(h5files) > 1 and self.filename is None:
            self.find_metadata_status_label.value = (
                "Multiple h5 files found in this"
                + " directory. Choose one with the file browser."
            )
            self.import_button.disable()
            return
        self.projections.metadata = self.reset_metadata_to()
        self.projections.import_metadata(self.filedir / self.filename)
        self.projections.metadata.metadata_to_DataFrame()
        with self.metadata_table_output:
            self.metadata_table_output.clear_output(wait=True)
            display(self.projections.metadata.dataframe)
            self.import_button.enable()

    def create_app(self):
        self.app = HBox(
            [
                VBox(
                    [
                        self.quick_path_label,
                        HBox(
                            [
                                self.quick_path_search,
                                self.import_button.button,
                            ]
                        ),
                        self.filechooser,
                    ],
                ),
                self.viewer.app,
            ],
            layout=Layout(justify_content="center"),
        )

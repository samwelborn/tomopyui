import pathlib

import numpy as np
import solara
import solara.lab

from ..components.importer import Importer
from ..components.viewer.slicer import ThreeDSlicer
from ..context import ImageProvider, global_update_images

# Assuming the Importer component has been properly defined to handle file importation


@solara.component
def ImportPage():
    def on_import(path: pathlib.Path):
        print(f"Importing data from {path}")
        loaded_image_data = load_image_data(path)
        setNewImages(loaded_image_data)  # Update the global image context

    with solara.lab.Tabs():
        with solara.lab.Tab("Import"):
            with solara.HBox():
                with solara.Card(title="Import", style="width: 40%; min-width: 3"):
                    Importer(on_import=on_import, file_types=[".tif", ".tiff"])
                    # with solara.Card(title="Viewer", style="width: 75%; min-width: 3"):
                    ImageProvider(children=ThreeDSlicer())
        with solara.lab.Tab("Center"):
            Importer(on_import=on_import, file_types=[".tif", ".tiff"])


def load_image_data(path: pathlib.Path) -> np.ndarray:
    # Placeholder function: Implement the actual logic to load and return image data from the given path
    # For demonstration, this just returns a random numpy array
    return np.random.rand(10, 256, 256)


def setNewImages(new_images: np.ndarray):
    if global_update_images:
        global_update_images(new_images)
    else:
        print("Error: The update function is not set.")


# Note: Ensure that the `Importer` component is properly implemented to handle the import process,
# including invoking the `on_import` callback with the selected file path.

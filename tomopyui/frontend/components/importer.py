from typing import Callable, Coroutine, Optional, Union
import solara
from .filechooser_quicksearch import FileBrowserSearch
from .buttons.reactive import ReactiveButton
import pathlib
from reacton.core import use_state, component


import solara


@component
def Importer(
    on_import: Callable[[pathlib.Path], Union[None, Coroutine]],
    file_types: Optional[list] = None,
):
    # State for managing the current directory and selected file path
    directory, set_directory = use_state(pathlib.Path("~/").expanduser())
    selected_file, set_selected_file = use_state(pathlib.Path())

    def handle_import():
        if selected_file:
            on_import(selected_file)

    with solara.VBox() as vbox:
        ReactiveButton(
            label="Import",
            on_click=handle_import,
            icon_name="fas fa-upload",
            disabled=selected_file is None,
        )
        FileBrowserSearch(
            start_directory=directory,
            on_file_select=set_selected_file,
            file_types=file_types,
        )

    return vbox

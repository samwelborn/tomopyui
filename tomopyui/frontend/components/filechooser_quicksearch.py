from pathlib import Path
from typing import Optional, Union, cast, Callable, List
import solara
from reacton.core import use_state, component
from reacton.core import component


@component
def FileBrowserSearch(
    start_directory: Union[None, str, Path, solara.Reactive[Path]] = None,
    on_file_select: Optional[Callable[[Path], None]] = None,
    file_types: Optional[List[str]] = None,  # Added parameter for file type filtering
):
    directory, set_directory = use_state(start_directory or Path("~/").expanduser())
    selected_path, set_selected_path = use_state(cast(Optional[Path], None))
    search_path, set_search_path = use_state("")

    # Define a filter function based on the file_types list
    def file_filter(path: Path) -> bool:
        if file_types is None:
            return True  # Show all files if no filter is provided
        if path.is_dir():
            return True  # Always show directories
        return any(path.name.endswith(file_type) for file_type in file_types)

    def handle_directory_change(new_directory: Path):
        set_directory(new_directory)
        set_selected_path(None)  # Reset selected path when changing directories

    def handle_file_open(file_path: Path):
        set_selected_path(file_path)
        if on_file_select:
            on_file_select(file_path)

    def handle_path_select(path: Optional[Path]):
        set_selected_path(path)
        if on_file_select:
            on_file_select(path)

    def update_search_path(new_path: str):
        if new_path:
            try:
                path_obj = Path(new_path).expanduser().resolve()
                if path_obj.exists():
                    if path_obj.is_dir():
                        set_directory(path_obj)
                    else:
                        set_directory(path_obj.parent)
                        set_selected_path(path_obj)
                set_search_path(new_path)
            except Exception as e:
                print(f"Error updating path: {e}")

    with solara.VBox():
        solara.InputText(
            "Search or Enter Path", value=search_path, on_value=update_search_path
        )
        solara.Button("Clear", on_click=lambda: set_search_path(""))

        solara.FileBrowser(
            directory=directory,
            on_directory_change=handle_directory_change,
            on_path_select=handle_path_select,
            on_file_open=handle_file_open,
            can_select=False,
            filter=file_filter
        )
        if selected_path:
            solara.Info(f"You selected: {selected_path}")

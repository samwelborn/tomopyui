from typing import List

import bqplot as bq
import reacton
import reacton.ipywidgets as widgets
from pydantic import BaseModel


class DropdownProps(BaseModel):
    name: str
    description: str
    options: List[str]
    value: str


@reacton.component
def SchemeDropdown(im_props: ImageProps) -> widgets.Dropdown:
    lin_schemes: List[str] = [
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "OrRd",
        "PuBu",
        "BuPu",
        "Oranges",
        "BuGn",
        "YlOrBr",
        "YlGn",
        "Reds",
        "RdPu",
        "Greens",
        "YlGnBu",
        "Purples",
        "GnBu",
        "Greys",
        "YlOrRd",
        "PuRd",
        "Blues",
        "PuBuGn",
    ]

    value, set_value = reacton.use_state("viridis")

    def update_scheme(change) -> None:
        """
        Updates the scheme based on dropdown value selection.
        """
        im_props.scale_image.scheme = change["new"]

    dd: widgets.Dropdown = widgets.Dropdown(
        description="Scheme: ", options=lin_schemes, value=value
    )

    def attach_event_handler():
        """
        Attaches the update_scheme function to the dropdown change event.
        """
        dd_widget = reacton.get_widget(dd)

        def on_value_change(change) -> None:
            update_scheme(change)

        def cleanup() -> None:
            dd_widget.unobserve(on_value_change, names="value")

        dd_widget.observe(on_value_change, names="value")

        return cleanup

    reacton.use_effect(attach_event_handler)

    return dd

from typing import Callable

import reacton
import reacton.ipywidgets as w
from pydantic import ConfigDict
from .simple import ButtonProps


class OnOffButtonProps(ButtonProps):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    on: bool
    on_click: Callable[[], None]


@reacton.component
def OnOffButton(props: OnOffButtonProps):
    button_style = "success" if props.on else ""

    def on_click_wrapper():
        props.on_click()

    return w.Button(
        icon=props.icon,
        tooltip=props.tooltip,
        on_click=on_click_wrapper,
        button_style=button_style,
        style=props.style,
        layout=props.layout,
    )

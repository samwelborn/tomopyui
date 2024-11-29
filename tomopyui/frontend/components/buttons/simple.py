from typing import Callable, Any, Optional

import reacton
import reacton.ipywidgets as w
from pydantic import BaseModel


class ButtonProps(BaseModel):
    name: Optional[str] = None
    icon: str = "far square"
    tooltip: str = ""
    layout: dict = {"width": "45px", "height": "40px"}
    style: dict = {"font_size": "22px"}


@reacton.component
def ButtonSimpleCallback(props: ButtonProps, on_click: Callable[[], Any]):

    button = w.Button(
        icon=props.icon,
        tooltip=props.tooltip,
        on_click=on_click,
        style=props.style,
        layout=props.layout,
    )

    return button

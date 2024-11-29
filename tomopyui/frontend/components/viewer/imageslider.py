from typing import Callable, Optional

import numpy as np
import reacton
import reacton.ipywidgets as widgets
from pydantic import BaseModel
import solara

from ...context import ImageContext


class ImageSliderProps(BaseModel):
    images: list
    image_index: int
    set_image_index: Callable[[int], None]


@reacton.component
def ImageSlider(props: ImageSliderProps):
    context = reacton.use_context(ImageContext)
    images = context["images"]
    image_index = props.image_index

    slider = solara.SliderInt(
        label="Image Index:",
        value=image_index,
        min=0,
        max=len(images) - 1,
        step=1,
        on_value=props.set_image_index,
    )

    return slider

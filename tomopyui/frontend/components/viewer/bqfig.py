from typing import Any, List, Optional, Type, Union

import bqplot as bq
import numpy as np
import reacton
import reacton.bqplot as rbq
import reacton.ipywidgets as widgets
import reacton.ipywidgets as w
import reacton.ipywidgets as rw
import solara
from bqplot.scales import ColorScale, LinearScale, Scale
from bqplot_image_gl import ImageGL
from bqplot_image_gl.interacts import MouseInteraction, keyboard_events, mouse_events
from bs4 import BeautifulStoneSoup
from pydantic import BaseModel, ConfigDict, Field
from reacton.bqplot import PanZoom
from reacton.core import Element, use_effect, use_memo, use_ref

from ...context import ImageContext
from .histogram import Histogram


class ImageProps(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    scale_x: Optional[Scale] = Field(default_factory=lambda: LinearScale(min=0, max=1))
    scale_y: Optional[Scale] = Field(default_factory=lambda: LinearScale(min=1, max=0))
    scale_image: Optional[ColorScale] = Field(
        default_factory=lambda: ColorScale(min=0, max=1, scheme="viridis")
    )

    def dict(self):
        d = {
            "x": self.scale_x,
            "y": self.scale_y,
            "image": self.scale_image,
        }
        return d


class FigureLayoutProps(BaseModel):
    width: str = "100%"
    height: str = "100%"
    fig_margin: dict[str, float] = dict(top=0, bottom=0, left=0, right=0)


class DefaultFigureProps(BaseModel):
    padding_x: float = 0
    padding_y: float = 0
    pixel_ratio: float = 1.0
    fig_margin: dict[str, float] = dict(top=0, bottom=0, left=0, right=0)
    layout: FigureLayoutProps = FigureLayoutProps()


class FigureProps(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    index: int = 0
    images: np.ndarray
    vmin: float
    vmax: float
    padding_x: float = 0
    padding_y: float = 0
    fig_margin: dict[str, float] = dict(top=0, bottom=0, left=0, right=0)
    layout: FigureLayoutProps = FigureLayoutProps()


@reacton.component
def BqFigure(images: np.ndarray, index: int, vmin: float, vmax: float):
    vmin_value, _ = reacton.use_state(vmin)
    vmax_value, _ = reacton.use_state(vmax)

    image_scale = bq.ColorScale(min=vmin_value, max=vmax_value, scheme="viridis")

    im_props = ImageProps(
        scale_image=image_scale,
    )

    # hist = Histogram(images=images)

    im = reacton.use_memo(
        lambda: ImageGL(image=images[index], scales=im_props.dict()), []
    )
    figure = reacton.use_memo(
        lambda: bq.Figure(
            scale_x=im_props.scale_x,
            scale_y=im_props.scale_y,
            marks=[im],
            **DefaultFigureProps().model_dump(),
        ),
        [],
    )

    def on_change_colors():
        im.scales["image"].min = vmin_value
        im.scales["image"].max = vmax_value

    def change_aspect_ratio():
        figure.min_aspect_ratio = images.shape[2] / images.shape[1]
        figure.max_aspect_ratio = images.shape[2] / images.shape[1]

    def on_change_index():
        im.image = images[index]

    def on_new_images():
        change_aspect_ratio()
        im.image = images[0]

    reacton.use_effect(on_change_colors, [vmin_value, vmax_value])
    reacton.use_effect(on_change_index, [index])
    reacton.use_effect(on_new_images, [images])

    return rw.Box(children=[figure])

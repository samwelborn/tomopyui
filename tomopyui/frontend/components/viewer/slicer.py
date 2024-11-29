import reacton
import reacton.bqplot as rbq
import solara
from bqplot.scales import LinearScale
from bqplot_image_gl.interacts import BrushSelector, MouseInteraction
import solara

from ...context import ImageContext
from ..buttons.onoff import OnOffButton, OnOffButtonProps
from ..buttons.simple import ButtonProps, ButtonSimpleCallback
from .bqfig import FigureComponent, FigureProps
from .imageslider import ImageSlider, ImageSliderProps


@reacton.component
def ThreeDSlicer():
    image_index, set_image_index = reacton.use_state(0)
    context = reacton.use_context(ImageContext)
    images = context["images"]

    scale_x = rbq.LinearScale(min=0, max=1)
    scale_y = rbq.LinearScale(min=1, max=0)
    # scale_x, scale_y = reacton.use_memo(
    #     lambda: (LinearScale(min=0, max=1), LinearScale(min=1, max=0)), []
    # )

    play_speed, set_play_speed = reacton.use_state(300)

    # Managing which interaction is currently active
    is_rectangle_mode, set_is_rectangle_mode = reacton.use_state(False)

    def toggle_interaction_mode():
        set_is_rectangle_mode(not is_rectangle_mode)

    figure_props = FigureProps(
        images=images,
        index=image_index,
        scale_x=scale_x,
        scale_y=scale_y,
    )

    figure = FigureComponent(props=figure_props)
    slider = ImageSlider(
        ImageSliderProps(
            images=images, image_index=image_index, set_image_index=set_image_index
        )
    )

    rectangle_selector_button = OnOffButton(
        OnOffButtonProps(
            icon="far square", on=is_rectangle_mode, on_click=toggle_interaction_mode
        )
    )

    def on_plus():
        set_play_speed(play_speed + 50)

    def on_minus():
        set_play_speed(play_speed - 50)

    speed_up = ButtonSimpleCallback(
        ButtonProps(icon="plus", tooltip="Increase play speed"), on_click=on_plus
    )
    slow_down = ButtonSimpleCallback(
        ButtonProps(icon="minus", tooltip="Decrease play speed"), on_click=on_minus
    )

    with solara.lab
    with solara.VBox(grow=False, align_items="center"):
        solara.VBox([figure, slider], grow=False)
        solara.HBox([speed_up, slow_down, rectangle_selector_button])

import asyncio
import json
from turtle import fillcolor
from typing import Callable, Optional

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import reacton.ipywidgets as w
import solara
from reacton.core import use_effect, use_state

from tomopyui.widgets.helpers import debounce


class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for Plotly objects.

    Plotly may return objects that the standard JSON encoder can't handle. This
    encoder converts such objects to str, allowing serialization by json.dumps
    """

    def default(self, o):
        if isinstance(o, object):
            return ""
        return super().default(o)


@solara.component
def Plotly(
    images: np.ndarray,
    index: int,
    vmin: float,
    vmax: float,
    on_set_px_range: Callable[[list[int], list[int]], None],
):

    current_image, set_current_image = use_state(images[0])

    def update_image():
        set_current_image(images[index])

    use_effect(update_image, [index])

    def on_relayout(data):
        if data is None:
            return

        relayout_data = data["relayout_data"]

        # Check for xaxis and yaxis range updates in the relayout_data
        if "xaxis.range[0]" in relayout_data and "xaxis.range[1]" in relayout_data:
            xaxis_range = [
                relayout_data["xaxis.range[0]"],
                relayout_data["xaxis.range[1]"],
            ]
            print("X-axis range after zoom/pan:", xaxis_range)

        if "yaxis.range[0]" in relayout_data and "yaxis.range[1]" in relayout_data:
            yaxis_range = [
                relayout_data["yaxis.range[0]"],
                relayout_data["yaxis.range[1]"],
            ]
            print("Y-axis range after zoom/pan:", yaxis_range)

        if "selections" in relayout_data and relayout_data["selections"]:
            # Assuming there's only one selection to handle at a time
            selection = relayout_data["selections"][0]
            x0, x1 = selection["x0"], selection["x1"]
            y0, y1 = selection["y0"], selection["y1"]

            # Ensure x0 < x1 and y0 < y1 by swapping if necessary
            x0, x1 = sorted([x0, x1])
            y0, y1 = sorted([y0, y1])

            _, max_height, max_width = images.shape
            x_range_corr = [
                max(0, min(x0, max_width - 1)),
                max(0, min(x1, max_width - 1)),
            ]
            y_range_corr = [
                max(0, min(y0, max_height - 1)),
                max(0, min(y1, max_height - 1)),
            ]

            # Use the corrected ranges
            on_set_px_range(x_range_corr, y_range_corr)

    layout, set_layout = use_state(
        go.Layout(
            showlegend=False,
            autosize=False,
            width=400,
            height=320,
            hovermode="closest",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                visible=False,
                range=[0, images.shape[2] - 1],
                # minallowed=0,
                # maxallowed=images.shape[2],
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                visible=False,
                range=[images.shape[1] - 1, 0],
                scaleanchor="x",
                scaleratio=1,
                # minallowed=0,
                # maxallowed=images.shape[1],
            ),
            dragmode="zoom",
            modebar=go.layout.Modebar(add=["deselect"], remove=["lasso"]),
        )
    )

    heat = go.FigureWidget(
        data=[
            go.Scatter(
                x=[0],
                y=[0],
            ),
            go.Heatmap(z=current_image, colorscale="Viridis"),
        ],
        layout=layout,
    )

    solara.FigurePlotly(
        heat,
        on_relayout=on_relayout,
        dependencies=[current_image],
    )

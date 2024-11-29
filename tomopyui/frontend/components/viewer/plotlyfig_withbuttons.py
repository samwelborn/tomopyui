import asyncio
import json
from turtle import fillcolor

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
def Plotly(images: np.ndarray, index: int, vmin: float, vmax: float):

    current_image, set_current_image = use_state(images[0])

    def update_image():
        set_current_image(images[index])

    use_effect(update_image, [index])

    def on_relayout(data):
        if data is None:
            return

        relayout_data = data["relayout_data"]
        print(select_data)

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

    button_layer_1_height = 1.4
    button_layer_2_height = 1.2
    layout, set_layout = use_state(
        go.Layout(
            showlegend=False,
            autosize=False,
            width=400,
            height=400,
            margin=dict(l=20, r=20, t=0, b=20),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            dragmode="select",
            modebar=go.layout.Modebar(add=["deselect"], remove=["lasso"]),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list(
                        [
                            dict(
                                args=["type", "surface"],
                                label="3D Surface",
                                method="restyle",
                            ),
                            dict(
                                args=["type", "heatmap"],
                                label="Heatmap",
                                method="restyle",
                            ),
                        ]
                    ),
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.11,
                    xanchor="left",
                    y=button_layer_2_height,
                    yanchor="top",
                ),
                dict(
                    buttons=list(
                        [
                            dict(
                                args=["colorscale", "Viridis"],
                                label="Viridis",
                                method="restyle",
                            ),
                            dict(
                                args=["colorscale", "Cividis"],
                                label="Cividis",
                                method="restyle",
                            ),
                            dict(
                                args=["colorscale", "Blues"],
                                label="Blues",
                                method="restyle",
                            ),
                            dict(
                                args=["colorscale", "Greens"],
                                label="Greens",
                                method="restyle",
                            ),
                        ]
                    ),
                    type="buttons",
                    direction="right",
                    pad={"r": 2, "t": 2},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=button_layer_1_height,
                    yanchor="top",
                ),
            ],
            annotations=[
                dict(
                    text="colorscale",
                    x=0,
                    xref="paper",
                    y=1.1,
                    yref="paper",
                    align="left",
                    showarrow=False,
                ),
                dict(
                    text="Reverse<br>Colorscale",
                    x=0,
                    xref="paper",
                    y=1.06,
                    yref="paper",
                    showarrow=False,
                ),
                dict(
                    text="Lines",
                    x=0.47,
                    xref="paper",
                    y=1.045,
                    yref="paper",
                    showarrow=False,
                ),
            ],
        )
    )

    select_data, set_select_data = use_state(None)

    heat = go.FigureWidget(
        data=[
            go.Heatmap(z=current_image, colorscale="Viridis"),
            go.Scatter(
                x=[0],
                y=[0],
            ),
        ],
        layout=layout,
    )

    with solara.VBox() as main:
        solara.FigurePlotly(
            heat,
            on_relayout=on_relayout,
            on_selection=set_select_data,
            dependencies=[current_image],
        )

    return main

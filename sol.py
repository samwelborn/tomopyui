import asyncio
from functools import partial

import numpy as np
import solara
from bqplot import LinearScale
from exceptiongroup import catch
from reacton import ipywidgets as rw
from reacton import use_state
from solara.lab import Tab, Tabs, task, use_task

from tomopyui.backend.schemas.prenorm_input import PrenormProjectionsMetadataNew
from tomopyui.frontend.components.filechooser_quicksearch import FileBrowserSearch
from tomopyui.frontend.components.metadata.metadata import PydanticForm, PydanticTable
from tomopyui.frontend.components.viewer.bqfig import BqFigure
from tomopyui.frontend.components.viewer.h5viewer import H5Viewer
from tomopyui.frontend.components.viewer.plotlyfig import Plotly

# from tomopyui.backend.io import Projections_Prenormalized

# from tomopyui.frontend.pages.imports import ImportPage

# @solara.component
# def Page():
#     return ImportPage()

# Page()


num_images = 20
x = np.linspace(-1, 1, 128)
y = np.linspace(-1, 1, 128)
X, Y = np.meshgrid(x, y)

image_data = np.array(
    [np.cos(X**2 + Y**2 + phase) for phase in np.linspace(0, 2 * np.pi, num_images)]
).astype(np.float32)

types_of_data = ["tiff file", "tiff folder"]


@task(prefer_threaded=False)
async def debounce_update(value):
    await asyncio.sleep(1)
    return value


@solara.component
def Page():

    im_idx, set_im_idx = use_state(0)
    plotly_im_idx, set_plotly_im_idx = use_state(0)
    px_range, set_px_range = use_state([[0, 1], [0, 1]])
    data_type, set_data_type = use_state("tiff file")
    projections, set_projections = use_state(image_data)
    metadata, set_metadata = use_state(None)

    def on_slider_change(value):
        set_im_idx(value)
        debounce_update(value)

    if debounce_update.finished:
        new_idx = debounce_update.value
        if new_idx == im_idx:
            set_plotly_im_idx(new_idx)

    def on_switch_to_movie():
        set_switch_to_movie(not switch_to_movie)
        set_movie_button_label(
            "Switch to Movie" if switch_to_movie else "Switch to Image"
        )

    movie_button_label, set_movie_button_label = use_state("Switch to Movie")
    # switch_to_movie, set_switch_to_movie = use_state(False)
    # switch_to_movie_button = solara.Button(
    #     label=movie_button_label,
    #     on_click=on_switch_to_movie,
    # )

    entire_directory, set_entire_directory = use_state(False)

    def on_set_px_range(px_range_x, px_range_y):
        px_range_x = [int(px_range_x[0]), int(px_range_x[1])]
        px_range_y = [int(px_range_y[0]), int(px_range_y[1])]
        set_px_range([px_range_x, px_range_y])

    metadata_instance, set_metadata_instance = use_state(None)
    with solara.AppLayout(title="TomopyUI") as main:

        with solara.VBox() as sidebar:
            solara.Markdown("## Data Type")
            solara.Switch(
                label="Entire Directory",
                value=entire_directory,
                on_value=set_entire_directory,
            )
            solara.ToggleButtonsSingle(
                value=data_type, values=types_of_data, on_value=set_data_type
            )
            solara.Markdown("## File browser")
            with solara.Card():
                FileBrowserSearch()

            solara.Button("Upload Data")

        with solara.Card(title="Metadata input") as metadata_input:
            with solara.HBox():
                PydanticForm(
                    PrenormProjectionsMetadataNew,
                    model_instance=metadata_instance,
                    on_change=set_metadata_instance,
                )
                PydanticTable(metadata_instance)

        with solara.Card(title="Image Viewer") as image_slider:
            with rw.HBox(
                layout={
                    "justify_content": "center",
                    "align_items": "center",
                    "flex_wrap": "wrap",
                }
            ) as image_viewer:
                Plotly(image_data, plotly_im_idx, 0, 1, on_set_px_range)
                BqFigure(
                    images=image_data,
                    index=im_idx,
                    vmin=0,
                    vmax=1,
                )
            # solara.display(switch_to_movie_button)

            solara.SliderInt(
                label="Image Index",
                min=0,
                max=len(image_data) - 1,
                step=1,
                value=im_idx,
                on_value=on_slider_change,
            )
            solara.Info(
                icon=False,
                label=f"Pixel ranges |  x -> {px_range[0]} | y -> {px_range[1]}",
                dense=True,
                outlined=False,
            )

    return main


Page()


"""# Image annotation with Solara

This example displays how to annotate images with different drawing tools in plotly figures. Use the canvas
below to draw shapes and visualize the canvas callback.


Check [plotly docs](https://dash.plotly.com/annotations) for more information about image annotation.
"""

# import numpy as np
# import reacton
# import reacton.bqplot as bqplot
# import solara
# from bqplot import Figure as BqFigure
# from bqplot import LinearScale as BqLinearScale
# from bqplot import Lines as BqLines
# from bqplot import PanZoom as BqPanZoom
# from bqplot.interacts import BrushSelector as BqBrushSelector
# from reacton.bqplot import (
#     Axis,
#     ColorAxis,
#     ColorScale,
#     Figure,
#     HeatMap,
#     LinearScale,
#     PanZoom,
# )
# from reacton.bqplot_image_gl import ImageGL
# from reacton.core import ComponentWidget, use_state

# num_images = 20  # Number of images in the stack
# x = np.linspace(-1, 1, 500)
# y = np.linspace(-1, 1, 500)
# X, Y = np.meshgrid(x, y)

# image_data = np.array(
#     [np.cos(X**2 + Y**2 + phase) for phase in np.linspace(0, 2 * np.pi, num_images)]
# )

# x = np.linspace(-5, 5, 200)
# y = np.linspace(-5, 5, 200)
# X, Y = np.meshgrid(x, y)
# color = np.cos(X**2 + Y**2)


# @solara.component
# def Page():
#     current_image_index, set_current_image_index = use_state(0)

#     # Scales for the HeatMap
#     x_sc, y_sc, col_sc = (
#         LinearScale(),
#         LinearScale(),
#         ColorScale(scheme="RdYlBu"),
#     )

#     x_sc_bqplot, y_sc_bqplot = (BqLinearScale(), BqLinearScale())
#     # Initial HeatMap with the first image in the stack
#     heat = ImageGL(
#         image=color,
#         scales={"x": x_sc, "y": y_sc, "image": col_sc},
#     )
#     ax_x = Axis(scale=x_sc)
#     ax_y = Axis(scale=y_sc, orientation="vertical")
#     ax_c = ColorAxis(scale=col_sc)

#     panzoom = BqPanZoom(scales={"x": [x_sc_bqplot], "y": [y_sc_bqplot]})

#     # Create the figure with initial HeatMap
#     fig = Figure(
#         scale_x=x_sc,
#         scale_y=y_sc,
#         # scale_x=x_sc,
#         # scale_y=y_sc,
#         # axes=[ax_x, ax_y, ax_c],
#         title="Cosine",
#         min_aspect_ratio=1,
#         max_aspect_ratio=1,
#         padding_y=0,
#         marks=[heat],
#     )
#     fig.component.widget.interaction = panzoom

#     def on_slider_change(value):
#         # Update the current image index state
#         set_current_image_index(value)
#         # Update the HeatMap's color data with the new image

#     slider = solara.SliderInt(
#         label="Image Index",
#         min=0,
#         max=len(color) - 1,
#         step=1,
#         value=current_image_index,
#         on_value=on_slider_change,
#     )

#     return solara.VBox([slider, fig])


# x0 = np.linspace(0, 2, 100)

# exponent = solara.reactive(1.0)
# log_scale = solara.reactive(False)


# @solara.component
# def Page(x=x0, ymax=5):
#     y = x**exponent.value
#     color = "red"
#     display_legend = True
#     label = "bqplot graph"

#     solara.SliderFloat(value=exponent, min=0.1, max=3, label="Exponent")
#     solara.Checkbox(value=log_scale, label="Log scale")

#     # x_scale = bqplot.LinearScale(min=-5000, max=5000)
#     # if log_scale.value:
#     #     y_scale = bqplot.LogScale(min=0.1, max=ymax)
#     # else:
#     #     y_scale = bqplot.LinearScale(min=0, max=ymax)

#     # panzoom = bqplot.PanZoom(scales={"x": [x_scale], "y": [y_scale]})

#     # lines = bqplot.Lines(
#     #     x=x,
#     #     y=y,
#     #     scales={"x": x_scale, "y": y_scale},
#     #     stroke_width=3,
#     #     colors=[color],
#     #     display_legend=display_legend,
#     #     labels=[label],
#     # )

#     def on_brushing(change):
#         print(change)

#     bqscalex = BqLinearScale(min=-5000, max=5000)
#     bqscaley = BqLinearScale(min=0, max=ymax)
#     bqbrush = BqBrushSelector(
#         x_scale=bqscalex, y_scale=bqscaley, on_selected=on_brushing
#     )
#     bqbrush.observe(on_brushing, "brushing")

#     # brush = reacton.bqplot.BrushSelector(
#     #     x_scale=x_scale, y_scale=y_scale, on_selected=on_brushing
#     # )
#     # x_axis = reacton.bqplot.Axis(scale=x_scale)
#     # y_axis = reacton.bqplot.Axis(scale=y_scale, orientation="vertical")

#     fig_bq = BqFigure(
#         marks=[
#             BqLines(
#                 x=x,
#                 y=y,
#                 scales={"x": bqscalex, "y": bqscaley},
#                 stroke_width=3,
#                 colors=[color],
#                 display_legend=display_legend,
#                 labels=[label],
#             )
#         ],
#         scale_y=bqscaley,
#         scale_x=bqscalex,
#         interaction=bqbrush,
#     )

#     # fig = reacton.bqplot.Figure(
#     #     # axes=[x_axis, y_axis],
#     #     marks=[lines],
#     #     scale_y=x_scale,
#     #     scale_x=y_scale,
#     #     layout={"min_width": "800px"},
#     #     interaction=brush,
#     # )

#     with solara.VBox() as main:
#         solara.VBox([fig_bq])
#         solara.SliderFloat(value=exponent, min=0.1, max=3, label="Exponent")
#         solara.Checkbox(value=log_scale, label="Log scale")


# Page()


# # class CustomEncoder(json.JSONEncoder):
# #     """
# #     Custom JSON encoder for Plotly objects.

# #     Plotly may return objects that the standard JSON encoder can't handle. This
# #     encoder converts such objects to str, allowing serialization by json.dumps
# #     """

# #     def default(self, o):
# #         if isinstance(o, object):
# #             return str(o)
# #         return super().default(o)


# # @solara.component
# # def Page():

# #     current_image, set_current_image = use_state(image_data[0])
# #     print(current_image)

# #     def on_relayout(data):
# #         if data is None:
# #             return
# #         print(fig)

# #         relayout_data = data["relayout_data"]

# #         if "shapes" in relayout_data:
# #             shapes.value = relayout_data["shapes"]

# #         # Check for xaxis and yaxis range updates in the relayout_data
# #         if "xaxis.range[0]" in relayout_data and "xaxis.range[1]" in relayout_data:
# #             xaxis_range = [
# #                 relayout_data["xaxis.range[0]"],
# #                 relayout_data["xaxis.range[1]"],
# #             ]
# #             print("X-axis range after zoom/pan:", xaxis_range)

# #         if "yaxis.range[0]" in relayout_data and "yaxis.range[1]" in relayout_data:
# #             yaxis_range = [
# #                 relayout_data["yaxis.range[0]"],
# #                 relayout_data["yaxis.range[1]"],
# #             ]
# #             print("Y-axis range after zoom/pan:", yaxis_range)

# #         if "shapes" in relayout_data:
# #             shapes.value = relayout_data["shapes"]

# #     fig = go.FigureWidget(
# #         data=go.Heatmap(z=current_image, colorscale="Viridis"),
# #         layout=go.Layout(
# #             showlegend=True,
# #             autosize=False,
# #             width=600,
# #             height=600,
# #             margin=dict(l=20, r=20, t=20, b=20),
# #             xaxis=dict(showgrid=False, zeroline=False, visible=False),
# #             yaxis=dict(showgrid=False, zeroline=False, visible=False),
# #             dragmode="zoom",
# #             modebar={
# #                 "add": [
# #                     "drawrect",
# #                 ]
# #             },
# #         ),
# #     )

# #     def on_value(value):
# #         set_current_image(image_data[value])

# #     # sol_fig = solara.FigurePlotly(
# #     #     fig, on_relayout=on_relayout, dependencies=[current_image]
# #     # )
# #     slider = solara.SliderInt(
# #         label="",
# #         min=0,
# #         max=image_data.shape[0] - 1,
# #         step=1,
# #         on_value=on_value,
# #     )

# #     if not shapes.value:
# #         solara.Markdown("## Draw on the canvas")
# #     else:
# #         solara.Markdown("## Data returned by drawing")
# #         formatted_shapes = str(json.dumps(shapes.value, indent=2, cls=CustomEncoder))
# #         solara.Preformatted(formatted_shapes)


# # df = px.data.iris()
# # arr = np.random.random(100,100,100)
# # @solara.component
# # def Page():
# #     solara.provide_cross_filter()
# #     fig = px.histogram(df, "species")
# #     fig.update_layout(dragmode="select", selectdirection="h")

# #     with solara.VBox() as main:
# #         spx.density_heatmap(df, x="sepal_width", y="sepal_length")
# #         spx.scatter(df, x="sepal_width", y="sepal_length", color="species")
# #         spx.scatter_3d(df, x="sepal_width", y="sepal_length", z="petal_width")
# #         spx.CrossFilteredFigurePlotly(fig)
# #     return main

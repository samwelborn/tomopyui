import numpy as np
import reacton
import reacton.bqplot as rbq
from bqplot.interacts import BrushIntervalSelector
from bqplot.scales import LinearScale as BqLinearScale, Scale, ColorScale
from traitlets.utils.bunch import Bunch
from reacton.core import Element



@reacton.component
def Histogram(images: np.ndarray, image_colorscale: Element[ColorScale]):
    # Initialize state for vmin, vmax, and selector bounds
    vmin, setVmin = reacton.use_state(0.0)
    vmax, setVmax = reacton.use_state(1.0)
    selector_min, set_selector_min = reacton.use_state(0.0)
    selector_max, set_selector_max = reacton.use_state(1.0)

    selector_vmin, set_selector_vmin = reacton.use_state(0.0)
    selector_vmax, set_selector_vmax = reacton.use_state(1.0)

    # Compute histogram data (bin centers and frequencies)
    bin_centers = np.array([x for x in range(30)])
    bin_freqs = np.array([x for x in range(30)])

    # Initialize scales
    scale_x = rbq.LinearScale(min=vmin, max=vmax)
    scale_y = rbq.LinearScale()
    # brush_scale = reacton.use_memo(
    #     lambda: BqLinearScale(min=selector_min, max=selector_max),
    #     [selector_vmin, selector_vmax],
    # )

    # Create bars for the histogram
    bars = rbq.Bars(
        x=bin_centers,
        y=bin_freqs,
        scales={"x": scale_x, "y": scale_y},
        colors=["dodgerblue"],
        opacities=[0.75],
        orientation="horizontal",
    )

    # Define callback for brush selector changes
    def on_brush_select(change: Bunch):
        _brush = change["owner"]
        if _brush:
            sel: list[float] = _brush.selected
            print(sel)
            if all(sel):
                set_selector_vmin(sel[0])
                set_selector_vmax(sel[1])

    # Initialize brush selector for interaction
    # brush = BrushIntervalSelector(
    #     orientation="vertical",
    #     scale=brush_scale,
    # )

    # brush.observe(on_brush_select, "selected")

    # Create the figure
    figure = rbq.Figure(
        fig_margin=dict(top=0, bottom=0, left=0, right=0),
        layout={"width": "100px", "height": "100px"},
        marks=[bars],
        # interaction=brush,
    )

    # Effect to adjust vmin, vmax, and selector bounds based on image data
    def on_image_change():
        new_vmax = np.max(images)
        new_vmin = np.min(images)
        _min, _max = np.percentile(images, q=(0.5, 99.5))
        # Update state only if the values have changed
        if new_vmax != vmax or new_vmin != vmin:
            setVmax(new_vmax)
            setVmin(new_vmin)
        if _min != selector_min or _max != selector_max:
            set_selector_min(_min)
            set_selector_max(_max)

    reacton.use_effect(on_image_change, [images])
    # reacton.use_effect(on_brush_select, [brush.selected])
    return figure

    # def remove_bins_lower_than_min():
    #     ind = bin_centers < vmin
    #     bin_freqs[ind] = 0
    #     reacton.get_widget(scale_y) = float(np.max(bin_freqs))

    # def update_crange_selector(selected_range):
    #     if selector.selected is not None:
    #         image_scale["image"].min = selector.selected[0]
    #         image_scale["image"].max = selector.selected[1]
    #         vmin = selector.selected[0]
    #         vmax = selector.selected[1]

    # Use reacton hooks to manage state and effects
    # reacton.use_effect(refresh_histogram, [images])

    # Render the component using reacton components
    # (This is a placeholder; you'll need to replace it with the actual rendering logic)

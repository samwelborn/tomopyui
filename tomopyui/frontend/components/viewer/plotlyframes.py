import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import solara


@solara.component
def PlotlyAnimation(images: np.ndarray):

    # You can use solara.display directly
    fig = px.imshow(
        images,
        animation_frame=0,
    )
    solara.display(fig)

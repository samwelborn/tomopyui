from enum import Enum
from typing import Any, Callable, List, Optional, Type, get_args, get_origin

import pandas as pd
import reacton.ipywidgets as rw
import solara
from IPython.display import display
from ipywidgets import VBox
from jupyterlab_h5web import H5Web
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from reacton.core import component, use_effect, use_state


@component
def H5Viewer():
    # Convert the Pydantic model instance to a dictionary
    return rw.VBox(
        children=[
            H5Web(
                "/Users/swelborn/Documents/gits/tomopyui/examples/data/ALS_832_Data/fake_als_data.h5"
            )
        ]
    )

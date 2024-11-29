from enum import Enum
from typing import Any, Callable, List, Optional, Type, get_args, get_origin

import pandas as pd
import solara
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from reacton.core import component, use_effect, use_state


@component
def PydanticTable(model_instance: BaseModel):
    # Convert the Pydantic model instance to a dictionary
    if not model_instance:
        return solara.Text("No model instance provided")
    model_dict = model_instance.model_dump()

    # Create a DataFrame from the model dictionary
    # The DataFrame will have two columns: 'Field' and 'Value'
    data = {"Field": list(model_dict.keys()), "Value": list(model_dict.values())}
    df = pd.DataFrame(data)

    # Use Solara's DataFrame component to display the table
    return solara.DataFrame(df, items_per_page=10)


@component
def PydanticForm(
    model_cls: Type[BaseModel],
    model_instance: BaseModel,
    on_change: Callable[[BaseModel], None],
):
    fields = model_cls.model_fields

    def on_value_change(field_name: str):
        def inner(new_value: Any):
            on_change(model_cls(**{field_name: new_value}))

        return inner

    widgets = [
        create_widget(field=fields[field_name], on_value=on_value_change(field_name))
        for field_name in fields
    ]

    return solara.VBox(children=[widget for widget in widgets if widget is not None])


def create_widget(field: FieldInfo, on_value: Callable[[Any], None]):
    field_type, default = get_field_type_and_default(field)
    desc = field.description or ""

    # Check if the field is an enum and handle it with ToggleButtonsSingle
    if issubclass(field_type, Enum):
        return create_enum_widget(field_type, default, desc, on_value)

    # Mapping for other types
    type_to_widget = {
        int: solara.InputInt,
        float: solara.InputFloat,
        str: solara.InputText,
    }

    widget_creator = type_to_widget.get(field_type)
    if widget_creator:
        return widget_creator(label=desc, value=default, on_value=on_value)

    return None


def create_enum_widget(
    enum_type: Type[Enum],
    default_value: Any,
    description: str,
    on_value: Callable[[Any], None],
):
    choices = [e.value for e in enum_type]  # Assuming Enum values are used directly
    default_value = default_value if default_value in choices else choices[0]

    # Use Reacton's use_state to manage the selected enum value state
    selected_value, set_selected_value = use_state(default_value)

    # Call the provided on_value callback whenever the selected value changes
    def handle_value_change(new_value: Any):
        set_selected_value(new_value)
        on_value(new_value)

    return solara.VBox(
        children=[
            solara.Markdown(f"**{description}**"),
            solara.ToggleButtonsSingle(
                value=selected_value,
                values=choices,
                on_value=handle_value_change,
            ),
        ]
    )


def get_field_type_and_default(field_info: FieldInfo) -> tuple[Any, Any]:
    base_annotation = get_origin(field_info.annotation) or field_info.annotation
    args_annotation = get_args(field_info.annotation)
    is_optional = type(None) in args_annotation
    field_type = (
        args_annotation[0]
        if is_optional and len(args_annotation) > 1
        else base_annotation
    )

    # Determine a sensible default value
    default_value = 0 if field_type in [int, float] else ""
    return field_type, (
        field_info.default if field_info.default is not None else default_value
    )

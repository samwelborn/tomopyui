import solara
from typing import Callable, Coroutine, Union
import asyncio


@solara.component
def ReactiveButton(
    label: str = "",
    on_click: Callable[
        [], Union[None, Coroutine]
    ] = None,  # Expect a coroutine function
    icon_name: str = "fa-upload",
    disabled: bool = False,
    button_style: str = "",
    button_style_during: str = "info",
    button_style_after: str = "success",
    description_during: str = "",
    description_after: str = "",
    icon_during: str = "fas fa-cog fa-spin fa-lg",
    icon_after: str = "fa-check-square",
    warning_text: str = "That button click didn't work.",  # Avoid name clash with warning module
):
    state, set_state = solara.use_state("initial")
    click_event, set_click_event = solara.use_state(0)

    async def async_wrapper():
        set_state("during")
        try:
            if asyncio.iscoroutinefunction(on_click):
                await on_click()  # Await if on_click is a coroutine function
            else:
                on_click()  # Call directly if on_click is a regular function
            set_state("after")
        except Exception as e:
            set_state("warning")
            print("Warning:", warning_text)

    def handle_click_sync():
        asyncio.create_task(async_wrapper())

    current_label = label
    current_icon = icon_name
    current_color = button_style

    # Determine the current state of the button for rendering
    current_label, current_icon, current_color = label, icon_name, button_style
    if state == "during":
        current_label, current_icon, current_color = (
            description_during,
            icon_during,
            button_style_during,
        )
    elif state == "after":
        current_label, current_icon, current_color = (
            description_after,
            icon_after,
            button_style_after,
        )
    elif state == "warning":
        current_label, current_icon, current_color = (
            warning_text,
            "exclamation-triangle",
            "warning",
        )

    return solara.Button(
        label=current_label,
        on_click=handle_click_sync,
        icon_name=current_icon,
        disabled=disabled
        or state == "during",  # Optionally disable the button during operation
        color=current_color,
    )

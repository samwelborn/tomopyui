from typing import Any

import numpy as np
import reacton
from pydantic import BaseModel

global_update_images = None

ImageContext = reacton.create_context(
    {"images": np.random.rand(10, 256, 256), "setImages": None, "updateImages": None}
)


@reacton.component
def ImageProvider(children):
    images, setImages = reacton.use_state(np.random.rand(10, 256, 256))

    # This function will be passed down and can be used to update the images
    def updateImages(new_images):
        setImages(new_images)

    # Set the global reference
    global global_update_images
    global_update_images = updateImages

    ImageContext.provide(
        {"images": images, "setImages": setImages, "updateImages": updateImages}
    )

    return children


# @reacton.component
# def PixelRangeProvider(props):
#     image_context = reacton.use_context(ImageContext)
#     images: np.ndarray = image_context["images"]
#     shape: tuple = images.shape

#     px_range, set_px_range = reacton.use_state((0,))

#     # This function will be passed down and can be used to update the images
#     def updateImages(new_images):
#         setImages(new_images)

#     # Set the global reference
#     global global_update_images
#     global_update_images = updateImages

#     value = {"images": images, "setImages": setImages, "updateImages": updateImages}

#     ImageContext.provide(
#         {"value": value, "setImages": setImages, "updateImages": updateImages}
#     )

#     return props.children


# External function to update the images
def setNewImages(new_images):
    if global_update_images:
        global_update_images(new_images)
    else:
        print("Error: The update function is not set.")

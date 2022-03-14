import cupy as cp
import numpy as np
from cupyx.scipy import ndimage as ndi_cp


def shrink_projections(imagestack, high_energy, low_energy, num_batches, order=3):
    shrink_ratio = low_energy / high_energy
    _imagestack = np.array_split(imagestack, num_batches, axis=0)
    zoomed_image_cpu = []
    for batch in _imagestack:
        batch_gpu = cp.array(batch, dtype=cp.float32)
        zoomed_image_gpu = ndi_cp.zoom(
            batch_gpu, (1, shrink_ratio, shrink_ratio), order=order
        )
        zoomed_image_cpu.append(cp.asnumpy(zoomed_image_gpu))

    zoomed_image_cpu = np.concatenate(zoomed_image_cpu, axis=0)
    mempool = cp.get_default_memory_pool()
    mempool.free_all_blocks()
    return zoomed_image_cpu


def shrink_and_pad_projections(
    imagestack_low, imagestack_high, low_energy, high_energy, num_batches, order=3
):
    shrink_ratio = low_energy / high_energy
    _imagestack = np.array_split(imagestack_low, num_batches, axis=0)
    zoomed_image_cpu = []
    ref_shape = imagestack_high.shape
    for batch in _imagestack:
        batch_gpu = cp.array(batch, dtype=cp.float32)
        zoomed_image_gpu = ndi_cp.zoom(
            batch_gpu, (1, shrink_ratio, shrink_ratio), order=order
        )
        zoomed_image_gpu = pad_to_make_same_size_cp(batch_gpu, ref_shape)
        zoomed_image_cpu.append(cp.asnumpy(zoomed_image_gpu))

    zoomed_image_cpu = np.concatenate(zoomed_image_cpu, axis=0)
    mempool = cp.get_default_memory_pool()
    mempool.free_all_blocks()
    return zoomed_image_cpu


def pad_to_make_same_size_cp(imagestack_to_pad, ref_shape):
    to_pad_shape = imagestack_to_pad.shape
    diffshape = [y - x for x, y in zip(to_pad_shape, ref_shape)]
    diffshape[0] = 0
    diffshape = [
        [x / 2, x / 2] if x % 2 == 0 else [x / 2 + 0.5, x / 2 - 0.5] for x in diffshape
    ]
    pad = tuple([(int(x[0]), int(x[1])) for x in diffshape])
    imagestack_padded = cp.pad(imagestack_to_pad, pad)
    return imagestack_padded

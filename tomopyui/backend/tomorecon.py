from joblib import Parallel, delayed
from time import process_time, perf_counter, sleep
from skimage.registration import phase_cross_correlation
from skimage import transform
from tomopy.recon import wrappers
from tomopy.prep.alignment import scale as scale_tomo
from contextlib import nullcontext
from tomopy.recon import algorithm
from tomopy.misc.corr import circ_mask
from skimage.transform import rescale
from .util.metadata_io import save_metadata, load_metadata
from tomopy.recon import algorithm as tomopy_algorithm
from tomopyui.backend.tomoalign import TomoAlign

import tomopyui.tomocupy.recon.algorithm as tomocupy_algorithm
import tomopyui.backend.tomodata as td
import matplotlib.pyplot as plt
import datetime
import time
import json
import astra
import os
import tifffile as tf
import cupy as cp
import tomopy
import numpy as np


class TomoRecon(TomoAlign):
    """ """

    def __init__(self, Recon, Align=None):
        # -- Creating attributes for reconstruction calcs ---------------------
        self._set_attributes_from_frontend(Recon)
        self.tomo = td.TomoData(metadata=Recon.Import.metadata)
        self.recon = None
        self.wd_parent = Recon.Import.wd
        self.make_wd()
        self._main()

    def _set_attributes_from_frontend(self, Recon):
        self.Recon = Recon
        self.metadata = Recon.metadata.copy()
        self.partial = Recon.partial
        if self.partial:
            self.prj_range_x = Recon.prj_range_x
            self.prj_range_y = Recon.prj_range_y
        self.pad = (Recon.paddingX, Recon.paddingY)
        self.downsample = Recon.downsample
        if self.downsample:
            self.downsample_factor = Recon.downsample_factor
        else:
            self.downsample_factor = 1
        self.pad_ds = tuple([int(self.downsample_factor * x) for x in self.pad])
        self.center = Recon.center + self.pad_ds[0]
        self.num_iter = Recon.num_iter
        self.upsample_factor = Recon.upsample_factor

    def make_wd(self):
        now = datetime.datetime.now()
        os.chdir(self.wd_parent)
        dt_string = now.strftime("%Y%m%d-%H%M-")
        try:
            os.mkdir(dt_string + "recon")
            os.chdir(dt_string + "recon")
        except:
            os.mkdir(dt_string + "recon-1")
            os.chdir(dt_string + "recon-1")
        save_metadata("overall_recon_metadata.json", self.metadata)
        if self.metadata["save_opts"]["tomo_before"]:
            np.save("projections_before_alignment", self.tomo.prj_imgs)
        self.wd = os.getcwd()

    def save_reconstructed_data(self):
        now = datetime.datetime.now()
        dt_string = now.strftime("%Y%m%d-%H%M-")
        method_str = list(self.metadata["methods"].keys())[0]
        os.mkdir(dt_string + method_str)
        os.chdir(dt_string + method_str)
        save_metadata("metadata.json", self.metadata)

        if self.metadata["save_opts"]["tomo_before"]:
            if self.metadata["save_opts"]["npy"]:
                np.save("tomo", self.tomo.prj_imgs)
            if self.metadata["save_opts"]["tiff"]:
                tf.imwrite("tomo.tif", self.tomo.prj_imgs)
            if (
                not self.metadata["save_opts"]["tiff"]
                and not self.metadata["save_opts"]["npy"]
            ):
                tf.imwrite("tomo.tif", self.tomo.prj_imgs)
        if self.metadata["save_opts"]["recon"]:
            if self.metadata["save_opts"]["npy"]:
                np.save("recon", self.recon)
            if self.metadata["save_opts"]["tiff"]:
                tf.imwrite("recon.tif", self.recon)
            if (
                not self.metadata["save_opts"]["tiff"]
                and not self.metadata["save_opts"]["npy"]
            ):
                tf.imwrite("recon.tif", self.recon)

        os.chdir(self.wd)

    def reconstruct(self):

        # ensure it only runs on 1 thread for CUDA
        os.environ["TOMOPY_PYTHON_THREADS"] = "1"
        method_str = list(self.metadata["methods"].keys())[0]
        if method_str == "MLEM_CUDA":
            method_str = "EM_CUDA"

        # Initialization of reconstruction dataset
        tomo_shape = self.prjs.shape
        self.recon = np.empty(
            (tomo_shape[1], tomo_shape[2], tomo_shape[2]), dtype=np.float32
        )
        self.Recon.log.info("Starting" + method_str)

        # TODO: parsing recon method could be done in an Align method
        if method_str == "SIRT_Plugin":
            self.recon = tomocupy_algorithm.recon_sirt_plugin(
                self.prjs,
                self.tomo.theta,
                num_iter=self.num_iter,
                rec=self.recon,
                center=self.center,
            )
        elif method_str == "SIRT_3D":
            self.recon = tomocupy_algorithm.recon_sirt_3D(
                self.prjs,
                self.tomo.theta,
                num_iter=self.num_iter,
                rec=self.recon,
                center=self.center,
            )
        elif method_str == "CGLS_3D":
            self.recon = tomocupy_algorithm.recon_cgls_3D_allgpu(
                self.prjs,
                self.tomo.theta,
                num_iter=self.num_iter,
                rec=self.recon,
                center=self.center,
            )
        else:
            # Options go into kwargs which go into recon()
            kwargs = {}
            options = {
                "proj_type": "cuda",
                "method": method_str,
                "num_iter": self.num_iter,
                # TODO: "extra_options": {},
            }
            kwargs["options"] = options

            self.recon = tomopy_algorithm.recon(
                self.prjs,
                self.tomo.theta,
                algorithm=wrappers.astra,
                init_recon=self.recon,
                center=self.center,
                ncore=1,
                **kwargs,
            )
        return self

    def _main(self):
        """
        Reconstructs a TomoData object using options in GUI.
        """

        metadata_list = super().make_metadata_list()
        for i in range(len(metadata_list)):
            self.metadata = metadata_list[i]
            super().init_prj()
            tic = time.perf_counter()
            self.reconstruct()
            toc = time.perf_counter()

            self.metadata["reconstruction_time"] = {
                "seconds": toc - tic,
                "minutes": (toc - tic) / 60,
                "hours": (toc - tic) / 3600,
            }
            self.save_reconstructed_data()

# from __future__ import annotations
# import pathlib

# from typing import List, Optional, Union

# from pydantic import BaseModel

# # from .importing import Acquisition, PixelUnits

# class SSRL62C_Image(BaseModel):
#     image_width: int
#     image_height: int
#     number_of_images: int
#     ccd_pixel_size: float
#     data_type: int
#     exposure_time: List[float]
#     images_per_projection: List[int]
#     images_taken: int
#     camera_binning: int
#     pixel_size: float
#     thetas: List[float]
#     x_positions: List[float]
#     y_positions: List[float]
#     z_positions: List[float]

# class ScanInfo(BaseModel):
#     VERSION: int
#     ENERGY: int
#     TOMO: int
#     MOSAIC: int
#     MULTIEXPOSURE: int
#     NREPEATSCAN: int
#     WAITNSECS: int
#     NEXPOSURES: int
#     AVERAGEONTHEFLY: int
#     IMAGESPERPROJECTION: int
#     REFNEXPOSURES: int
#     REFEVERYEXPOSURES: int
#     REFABBA: int
#     REFAVERAGEONTHEFLY: int
#     REFDESPECKLEAVERAGE: int
#     APPLYREF: int
#     MOSAICUP: int
#     MOSAICDOWN: int
#     MOSAICLEFT: int
#     MOSAICRIGHT: int
#     MOSAICOVERLAP: int
#     MOSAICCENTRALTILE: int
#     FILES: List[str]
#     PROJECTION_METADATA: List[SSRL62C_Image]
#     FLAT_METADATA: List[SSRL62C_Image]


# class SSRL62C(Acquisition):
#     scan_info: dict
#     scan_info_path: pathlib.Path
#     run_script_path: pathlib.Path
#     flats_filenames: List[pathlib.Path]
#     projections_filenames: List[pathlib.Path]
#     scan_type: str
#     scan_order: Optional[int]
#     num_angles: int
#     angles_rad: List[float]
#     angles_deg: List[float]
#     start_angle: float
#     end_angle: float
#     binning: int
#     projections_exposure_time: float
#     references_exposure_time: float
#     all_raw_energies_float: List[float]
#     all_raw_energies_str: List[str]
#     all_raw_pixel_sizes: List[float]
#     pixel_size_from_scan_info: float
#     energy_units: str
#     pixel_units: PixelUnits
#     raw_projections_dtype: str
#     raw_projections_directory: pathlib.Path
#     data_hierarchy_level: int


# class Model(BaseModel):
#     metadata_type: str
#     data_hierarchy_level: int
#     scan_info: ScanInfo
#     scan_info_path: str
#     run_script_path: str
#     flats_filenames: List[str]
#     projections_filenames: List[str]
#     scan_type: str
#     scan_order: List[List[Union[int, str]]]
#     pxX: int
#     pxY: int
#     pxZ: int
#     num_angles: int
#     angles_rad: List[float]
#     angles_deg: List[float]
#     start_angle: float
#     end_angle: float
#     binning: int
#     projections_exposure_time: List[float]
#     references_exposure_time: List[float]
#     all_raw_energies_float: List[float]
#     all_raw_energies_str: List[str]
#     all_raw_pixel_sizes: List[float]
#     pixel_size_from_scan_info: float
#     energy_units: str
#     pixel_units: str
#     raw_projections_dtype: str
#     raw_projections_directory: str

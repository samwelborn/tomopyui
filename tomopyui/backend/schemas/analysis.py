
from __future__ import annotations
import datetime

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AnalysisOpts(BaseModel):
    downsample: bool
    ds_factor: int
    pyramid_level: int
    num_iter: int
    center: float
    pad: List[int]
    extra_options: Dict[str, Any]
    use_multiple_centers: bool
    px_range_x: List[int]
    px_range_y: List[int]
    
    
class ReconOpts(AnalysisOpts):
    pass


class AlignOpts(AnalysisOpts):
    shift_full_dataset_after: bool
    upsample_factor: int
    pre_alignment_iters: int
    num_batches: int
    use_subset_correlation: bool
    subset_x: List[int]
    subset_y: List[int]


class Algorithms(BaseModel):
    art: Optional[bool]
    bart: Optional[bool]
    fbp: Optional[bool]
    gridrec: Optional[bool]
    mlem: Optional[bool]
    osem: Optional[bool]
    ospml_hybrid: Optional[bool]
    ospml_quad: Optional[bool]
    pml_hybrid: Optional[bool]
    pml_quad: Optional[bool]
    sirt: Optional[bool]
    tv: Optional[bool]
    grad: Optional[bool]
    tikh: Optional[bool]
    FBP_CUDA: Optional[bool] = Field(..., alias='FBP CUDA')
    SIRT_CUDA: Optional[bool] = Field(..., alias='SIRT CUDA')
    SART_CUDA: Optional[bool] = Field(..., alias='SART CUDA')
    CGLS_CUDA: Optional[bool] = Field(..., alias='CGLS CUDA')
    MLEM_CUDA: Optional[bool] = Field(..., alias='MLEM CUDA')
    SIRT_Plugin: Optional[bool] = Field(..., alias='SIRT Plugin')
    SIRT_3D: Optional[bool] = Field(..., alias='SIRT 3D')


class SaveOpts(BaseModel):
    Reconstruction: bool
    tiff: bool
    hdf: bool


class AlignSaveOpts(BaseModel):
    Projections_Before_Alignment: bool = Field(
        ..., alias='Projections Before Alignment'
    )
    Projections_After_Alignment: bool = Field(..., alias='Projections After Alignment')
    Reconstruction: bool


class Align(BaseModel):
    opts: AlignOpts
    methods: Algorithms
    save_opts: SaveOpts
    copy_hists_from_parent: bool
    data_hierarchy_level: int
    analysis_time: datetime.timedelta
    convergence: List[float]
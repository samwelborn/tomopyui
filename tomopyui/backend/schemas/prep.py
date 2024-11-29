from __future__ import annotations
import datetime
from enum import Enum
import pathlib

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

class Prep(BaseModel):
    data_hierarchy_level: int
    prep_list: List[List[Union[str, List[int]]]]
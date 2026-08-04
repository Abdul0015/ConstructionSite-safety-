import json
import uuid
from datetime import datetime
from typing import List, Optional, Any, Union
from pydantic import BaseModel, ConfigDict, field_validator

class ZoneCreateRequest(BaseModel):
    name: str
    zone_type: str = "excavation"
    polygon_coords: Union[List[dict], str]  # List of {"x":..., "y":...} or JSON string
    camera_id: Optional[str] = None
    ppe_requirements: Optional[Union[List[str], str]] = None
    is_active: bool = True

    model_config = ConfigDict(extra='forbid')

    @field_validator('polygon_coords')
    @classmethod
    def validate_polygon_coords(cls, v: Any) -> str:
        if isinstance(v, str):
            try:
                coords = json.loads(v)
            except Exception:
                raise ValueError("polygon_coords string must be valid JSON")
        else:
            coords = v

        if not isinstance(coords, list):
            raise ValueError("polygon_coords must be a list of coordinate points")

        if len(coords) < 3:
            raise ValueError("polygon_coords must contain at least 3 points")

        # Validate non-degenerate polygon (reject duplicate points resulting in < 3 unique vertices)
        unique_points = set()
        for idx, pt in enumerate(coords):
            if isinstance(pt, dict):
                x, y = pt.get("x"), pt.get("y")
            elif isinstance(pt, (list, tuple)) and len(pt) >= 2:
                x, y = pt[0], pt[1]
            else:
                raise ValueError(f"Point at index {idx} is invalid: {pt}")

            if x is None or y is None:
                raise ValueError(f"Point at index {idx} missing x or y coordinate")

            unique_points.add((x, y))

        if len(unique_points) < 3:
            raise ValueError(f"Polygon is degenerate: expected at least 3 unique non-collinear vertices, got {len(unique_points)}")

        if isinstance(v, str):
            return v
        return json.dumps(coords)

    @field_validator('ppe_requirements')
    @classmethod
    def validate_ppe_requirements(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            return v
        return json.dumps(v)

class ZoneResponse(BaseModel):
    id: uuid.UUID
    name: str
    zone_type: str
    polygon_coords: str
    camera_id: Optional[str] = None
    ppe_requirements: Optional[str] = None
    is_active: bool
    created_by: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra='forbid')

from typing import Optional
from pydantic import BaseModel, ConfigDict

class SystemHealthStatus(BaseModel):
    cameras_online: int
    cameras_offline: int
    detection_pipeline_status: str

    model_config = ConfigDict(extra='forbid')

class DashboardSummaryResponse(BaseModel):
    worker_count: int
    ppe_compliance_rate: Optional[float] = None
    active_equipment_count: int
    total_delivery_count: int
    open_hazard_count: int
    flagged_discrepancy_count: int
    pending_escalations: int = 0
    system_health: SystemHealthStatus

    model_config = ConfigDict(extra='forbid')

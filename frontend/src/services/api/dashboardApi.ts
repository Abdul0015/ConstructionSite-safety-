export interface SystemHealthStatus {
  cameras_online: number;
  cameras_offline: number;
  detection_pipeline_status: string;
}

export interface DashboardSummary {
  worker_count: number;
  ppe_compliance_rate: number | null;
  active_equipment_count: number;
  total_delivery_count: number;
  open_hazard_count: number;
  flagged_discrepancy_count: number;
  pending_escalations: number;
  system_health: SystemHealthStatus;
}

const API_BASE = '/api/v1';

export async function fetchDashboardSummaryApi(token: string): Promise<DashboardSummary> {
  const res = await fetch(`${API_BASE}/dashboard/summary`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch dashboard summary.');
  }

  return res.json();
}

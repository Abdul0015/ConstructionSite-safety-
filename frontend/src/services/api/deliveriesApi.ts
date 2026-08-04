export interface DeliveryLog {
  id: string;
  gate_id?: string;
  reported_by?: string;
  ai_vehicle_count?: number | null;
  manual_reported_count: number;
  material_type: string;
  material_quantity: number;
  quantity_unit: string;
  vehicle_type?: string;
  discrepancy_flag: boolean;
  logged_at: string;
  discrepancy_resolved?: boolean;
  resolved_by?: string;
  resolved_at?: string;
}

export interface DeliveryLogCreatePayload {
  gate_id: string;
  manual_reported_count: number;
  material_type: string;
  material_quantity: number;
  quantity_unit: string;
  vehicle_type?: string;
}

export interface MaterialInflowSummary {
  material_type: string;
  total_quantity: number;
  quantity_unit: string;
  delivery_count: number;
}

const API_BASE = '/api/v1';

export async function createDeliveryLogApi(
  token: string,
  payload: DeliveryLogCreatePayload
): Promise<DeliveryLog> {
  const res = await fetch(`${API_BASE}/deliveries`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to log delivery entry.');
  }

  return res.json();
}

export async function fetchDiscrepanciesApi(token: string): Promise<DeliveryLog[]> {
  const res = await fetch(`${API_BASE}/deliveries/discrepancies`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch flagged discrepancies.');
  }

  return res.json();
}

export async function resolveDiscrepancyApi(
  token: string,
  id: string,
  action: 'resolve' | 'flag_for_investigation' = 'resolve',
  notes?: string
): Promise<DeliveryLog> {
  const res = await fetch(`${API_BASE}/deliveries/discrepancies/${id}/resolve`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ action, notes }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to resolve discrepancy.');
  }

  return data;
}

export async function fetchMaterialsSummaryApi(token: string): Promise<MaterialInflowSummary[]> {
  const res = await fetch(`${API_BASE}/deliveries/materials`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch material inflow log.');
  }

  return res.json();
}

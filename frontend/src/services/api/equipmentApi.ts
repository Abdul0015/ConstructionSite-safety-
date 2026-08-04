export interface Equipment {
  id: string;
  equipment_type: string;
  identifier?: string;
  location_description?: string;
  status: string;
  idle_minutes: number;
  last_detected_at?: string;
  created_at: string;
  updated_at: string;
}

const API_BASE = '/api/v1';

export async function fetchEquipmentApi(token: string): Promise<Equipment[]> {
  const res = await fetch(`${API_BASE}/equipment`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch equipment list.');
  }

  return res.json();
}

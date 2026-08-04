export interface Zone {
  id: string;
  name: string;
  zone_type: string;
  polygon_coords: string;
  camera_id?: string;
  ppe_requirements?: string;
  is_active: boolean;
  created_by?: string;
  created_at: string;
}

export interface ZoneCreatePayload {
  name: string;
  zone_type?: string;
  polygon_coords: any;
  camera_id?: string;
  ppe_requirements?: any;
  is_active?: boolean;
}

const API_BASE = '/api/v1';

export async function fetchZonesApi(token: string): Promise<Zone[]> {
  const res = await fetch(`${API_BASE}/zones`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch restricted zones.');
  }

  return res.json();
}

export async function createZoneApi(token: string, payload: ZoneCreatePayload): Promise<Zone> {
  const res = await fetch(`${API_BASE}/zones`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let errorMsg = 'Failed to create restricted zone.';
    if (typeof data.detail === 'string') {
      errorMsg = data.detail;
    } else if (Array.isArray(data.detail) && data.detail.length > 0) {
      errorMsg = data.detail.map((e: any) => e.msg).join(' | ');
    }
    throw new Error(errorMsg);
  }

  return data;
}

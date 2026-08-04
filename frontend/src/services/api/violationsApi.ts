export interface Violation {
  id: string;
  gate_id?: string;
  zone_id?: string;
  worker_id?: string;
  violation_type: string;
  helmet_missing: boolean;
  vest_missing: boolean;
  image_url?: string;
  detected_at: string;
  status?: string;
  acknowledged_by?: string;
  acknowledged_at?: string;
  notes?: string;
}

const API_BASE = '/api/v1';

export async function fetchViolationsApi(token: string, filters?: { violation_type?: string }): Promise<Violation[]> {
  const queryParams = new URLSearchParams();
  if (filters?.violation_type) {
    queryParams.append('violation_type', filters.violation_type);
  }

  const url = `${API_BASE}/violations${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch violations.');
  }

  return res.json();
}

export async function acknowledgeViolationApi(token: string, id: string, notes?: string): Promise<Violation> {
  const res = await fetch(`${API_BASE}/violations/${id}/acknowledge`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ notes }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = typeof data.detail === 'string' ? data.detail : 'Failed to acknowledge violation.';
    const err = new Error(errorMsg);
    (err as any).status = res.status;
    (err as any).detail = errorMsg;
    throw err;
  }

  return data;
}

export async function uploadVideoApi(token: string, file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/violations/process-video`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to upload and process video file.');
  }

  return data;
}

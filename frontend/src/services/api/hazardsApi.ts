export interface HazardReport {
  id: string;
  reported_by?: string;
  description: string;
  image_url?: string;
  location: string;
  category: string;
  created_at: string;
}

const API_BASE = '/api/v1';

export async function createHazardReportApi(
  token: string,
  formData: FormData
): Promise<HazardReport> {
  const res = await fetch(`${API_BASE}/hazard-reports`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to submit hazard report.');
  }

  return res.json();
}

export async function fetchHazardReportsApi(token: string): Promise<HazardReport[]> {
  const res = await fetch(`${API_BASE}/hazard-reports`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch hazard reports.');
  }

  return res.json();
}

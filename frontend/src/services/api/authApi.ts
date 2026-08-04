export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'supervisor' | 'worker';
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

const API_BASE = '/api/v1';

export async function loginApi(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed. Please check credentials.');
  }

  return res.json();
}

export async function fetchMeApi(token: string): Promise<UserProfile> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    throw new Error('Failed to fetch user profile.');
  }

  return res.json();
}

export async function refreshTokenApi(refreshToken: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!res.ok) {
    throw new Error('Refresh token invalid or revoked.');
  }

  return res.json();
}

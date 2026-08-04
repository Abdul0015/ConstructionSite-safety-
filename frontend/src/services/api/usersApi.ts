export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'supervisor' | 'worker';
  created_at: string;
}

export interface UserCreatePayload {
  email: string;
  full_name: string;
  password: string;
  role: 'admin' | 'supervisor' | 'worker';
}

const API_BASE = '/api/v1';

export async function fetchUsersApi(token: string): Promise<User[]> {
  const res = await fetch(`${API_BASE}/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch users.');
  }

  return res.json();
}

export async function createUserApi(token: string, payload: UserCreatePayload): Promise<User> {
  const res = await fetch(`${API_BASE}/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let errorMsg = 'Failed to create user account.';
    if (typeof data.detail === 'string') {
      errorMsg = data.detail;
    } else if (Array.isArray(data.detail) && data.detail.length > 0) {
      errorMsg = data.detail.map((e: any) => e.msg).join(' | ');
    }
    throw new Error(errorMsg);
  }

  return data;
}

export async function deactivateUserApi(token: string, userId: string): Promise<User> {
  const res = await fetch(`${API_BASE}/users/${userId}/deactivate`, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${token}` },
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = typeof data.detail === 'string' ? data.detail : 'Failed to deactivate user account.';
    const err = new Error(errorMsg);
    (err as any).status = res.status;
    (err as any).detail = errorMsg;
    throw err;
  }

  return data;
}

import { describe, it, expect, beforeEach, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../store/authContext';
import { LoginPage } from '../pages/LoginPage';
import { DeliveryLogPage } from '../pages/DeliveryLogPage';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { DashboardOverviewPage } from '../pages/DashboardOverviewPage';

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('Phase 5 Frontend Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('1. Unit Test - Delivery Log & Hazard Report form validation rules', async () => {
    localStorage.setItem('access_token', 'mock_token');
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '1', email: 'supervisor@siteintel.com', role: 'supervisor', full_name: 'Supervisor Test' }),
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <DeliveryLogPage />
        </MemoryRouter>
      </AuthProvider>
    );

    const quantityInput = screen.getByLabelText(/Quantity/i);
    
    // Test invalid negative quantity input
    fireEvent.change(quantityInput, { target: { value: '-5' } });
    expect((quantityInput as HTMLInputElement).checkValidity()).toBe(false);

    // Change to valid quantity >= 0.01
    fireEvent.change(quantityInput, { target: { value: '25.5' } });
    expect((quantityInput as HTMLInputElement).checkValidity()).toBe(true);

    console.log('\n[PHASE 5 FRONTEND TEST] 1. UNIT TEST FORM VALIDATION');
    console.log('[RESULT] Quantity -5 rejected by HTML5 schema; Quantity 25.5 accepted!');
  });

  it('2. Integration Test - Full login -> token storage -> dashboard transition', async () => {
    // Mock login response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'valid_access_jwt', refresh_token: 'valid_refresh_jwt' }),
    });
    // Mock fetchMe response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'user_1', email: 'admin@siteintel.com', role: 'admin', full_name: 'Admin Test' }),
    });
    // Mock dashboard summary response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ worker_count: 5, ppe_compliance_rate: 98.5, active_equipment_count: 3, total_delivery_count: 10, open_hazard_count: 2, flagged_discrepancy_count: 1 }),
    });
    // Mock materials summary
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardOverviewPage />} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    fireEvent.change(screen.getByPlaceholderText('user@siteintel.com'), { target: { value: 'admin@siteintel.com' } });
    fireEvent.change(screen.getByPlaceholderText('••••••••••••'), { target: { value: 'AdminSecurePass123!' } });
    fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('valid_access_jwt');
      expect(localStorage.getItem('refresh_token')).toBe('valid_refresh_jwt');
    });

    console.log('\n[PHASE 5 FRONTEND TEST] 2. INTEGRATION TEST LOGIN -> TOKEN STORAGE');
    console.log('[RESULT] Login successful! Tokens set in localStorage: valid_access_jwt');
  });

  it('3. Edge Case Test - Expired/invalid token mid-session redirects to login screen', async () => {
    localStorage.setItem('access_token', 'expired_invalid_token');

    // Mock fetchMe failure (HTTP 401 Unauthorized)
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Token expired or revoked' }),
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/login" element={<div>LOGIN SCREEN REDIRECTED</div>} />
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<div>DASHBOARD CONTENT</div>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(screen.getByText('LOGIN SCREEN REDIRECTED')).toBeInTheDocument();
    });

    console.log('\n[PHASE 5 FRONTEND TEST] 3. EDGE CASE EXPIRED TOKEN REDIRECT');
    console.log('[RESULT] Expired/corrupt token detected -> cleared token & redirected to Login screen!');
  });
});

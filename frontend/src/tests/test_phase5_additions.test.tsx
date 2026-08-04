import { describe, it, expect, beforeEach, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../store/authContext';

import { ViolationsPage } from '../pages/ViolationsPage';
import { DiscrepancyPage } from '../pages/DiscrepancyPage';
import { ZoneManagementPage } from '../pages/ZoneManagementPage';
import { EquipmentPage } from '../pages/EquipmentPage';
import { UserManagementPage } from '../pages/UserManagementPage';
import { DashboardOverviewPage } from '../pages/DashboardOverviewPage';

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('Phase 5 Frontend Additions Integration & Edge Case Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  const setupDynamicFetchMock = (role: 'admin' | 'supervisor' = 'admin', customHandlers: { [urlSubstr: string]: (options?: any) => Promise<any> } = {}) => {
    localStorage.setItem('access_token', 'mock_token');

    mockFetch.mockImplementation(async (url: string, options?: any) => {
      // 1. Auth Me Endpoint
      if (url.includes('/api/v1/auth/me')) {
        return {
          ok: true,
          json: async () => ({ id: 'user_1', email: 'test@siteintel.com', role, full_name: 'Test User' }),
        };
      }

      // 2. Custom endpoint handlers
      for (const pattern in customHandlers) {
        if (url.includes(pattern)) {
          return customHandlers[pattern](options);
        }
      }

      // 3. Fallback default
      return { ok: true, json: async () => [] };
    });
  };

  it('1. ViolationsPage - Renders real API response & Acknowledge 409 inline error', async () => {
    let acknowledgeCalled = false;

    setupDynamicFetchMock('supervisor', {
      '/api/v1/violations/viol_01/acknowledge': async () => {
        acknowledgeCalled = true;
        return {
          ok: false,
          status: 409,
          json: async () => ({ detail: 'Violation is already acknowledged' }),
        };
      },
      '/api/v1/violations': async () => ({
        ok: true,
        json: async () => [
          {
            id: 'viol_01',
            violation_type: 'ppe_missing',
            helmet_missing: true,
            vest_missing: false,
            detected_at: '2026-07-24T12:00:00Z',
            status: 'pending',
          },
        ],
      }),
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <ViolationsPage />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('ppe_missing')).toBeInTheDocument();
      expect(screen.getByTestId('violation-status-badge-viol_01')).toHaveTextContent('pending');
    });

    const ackBtn = screen.getByTestId('acknowledge-btn-viol_01');
    fireEvent.click(ackBtn);

    await waitFor(() => {
      expect(acknowledgeCalled).toBe(true);
      const errBanner = screen.getByTestId('ack-error-viol_01');
      expect(errBanner).toBeInTheDocument();
      expect(errBanner).toHaveTextContent('Violation is already acknowledged');
    });

    console.log('\n[PHASE 5 FRONTEND TEST 1] ViolationsPage acknowledge 409 inline error rendered cleanly!');
  });

  it('2. DiscrepancyPage - Admin resolves discrepancy & updates status badge', async () => {
    let resolveCalled = false;

    setupDynamicFetchMock('admin', {
      '/api/v1/deliveries/discrepancies/disc_01/resolve': async () => {
        resolveCalled = true;
        return {
          ok: true,
          json: async () => ({
            id: 'disc_01',
            discrepancy_resolved: true,
            resolved_by: 'user_1',
            resolved_at: '2026-07-24T12:05:00Z',
          }),
        };
      },
      '/api/v1/deliveries/discrepancies': async () => ({
        ok: true,
        json: async () => [
          {
            id: 'disc_01',
            ai_vehicle_count: 3,
            manual_reported_count: 2,
            material_type: 'sand',
            material_quantity: 15,
            quantity_unit: 'tons',
            discrepancy_flag: true,
            discrepancy_resolved: false,
            logged_at: '2026-07-24T12:00:00Z',
          },
        ],
      }),
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <DiscrepancyPage />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('UNRESOLVED MISMATCH')).toBeInTheDocument();
    });

    const resolveBtn = screen.getByTestId('resolve-btn-disc_01');
    fireEvent.click(resolveBtn);

    await waitFor(() => {
      expect(resolveCalled).toBe(true);
      expect(screen.getByTestId('discrepancy-status-badge-disc_01')).toHaveTextContent('RESOLVED');
    });

    console.log('\n[PHASE 5 FRONTEND TEST 2] DiscrepancyPage resolve flow updated badge to RESOLVED!');
  });

  it('3. ZoneManagementPage - Surfaces polygon validation error (< 3 points / degenerate)', async () => {
    let createZoneCalled = false;

    setupDynamicFetchMock('admin', {
      '/api/v1/zones': async (opts) => {
        if (opts && opts.method === 'POST') {
          createZoneCalled = true;
          return {
            ok: false,
            status: 422,
            json: async () => ({ detail: 'Polygon is degenerate: expected at least 3 unique non-collinear vertices, got 1' }),
          };
        }
        return { ok: true, json: async () => [] };
      },
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <ZoneManagementPage />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Configure New Restricted Zone')).toBeInTheDocument();
    });

    const nameInput = screen.getByPlaceholderText('e.g. Crane Heavy Lift Sector');
    fireEvent.change(nameInput, { target: { value: 'Test Degenerate Zone' } });

    const submitBtn = screen.getByRole('button', { name: /Save Zone Policy/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(createZoneCalled).toBe(true);
      const errBox = screen.getByTestId('zone-form-error');
      expect(errBox).toBeInTheDocument();
      expect(errBox).toHaveTextContent('Polygon is degenerate: expected at least 3 unique non-collinear vertices, got 1');
    });

    console.log('\n[PHASE 5 FRONTEND TEST 3] ZoneManagementPage surfaced backend polygon validation error cleanly!');
  });

  it('4. EquipmentPage - Renders real equipment list from backend', async () => {
    setupDynamicFetchMock('supervisor', {
      '/api/v1/equipment': async () => ({
        ok: true,
        json: async () => [
          {
            id: 'eq_01',
            equipment_type: 'excavator',
            identifier: 'EXC-001',
            location_description: 'Sector 4 Heavy Area',
            status: 'active',
            idle_minutes: 5,
            created_at: '2026-07-24T12:00:00Z',
            updated_at: '2026-07-24T12:05:00Z',
          },
        ],
      }),
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <EquipmentPage />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('EXC-001')).toBeInTheDocument();
      expect(screen.getByText('excavator')).toBeInTheDocument();
      expect(screen.getByText('5 min')).toBeInTheDocument();
    });

    console.log('\n[PHASE 5 FRONTEND TEST 4] EquipmentPage rendered equipment list from real backend endpoint!');
  });

  it('5. UserManagementPage - Admin self-deactivation 400 inline error banner', async () => {
    let deactivateCalled = false;

    setupDynamicFetchMock('admin', {
      '/api/v1/users/admin_id_100/deactivate': async () => {
        deactivateCalled = true;
        return {
          ok: false,
          status: 400,
          json: async () => ({ detail: 'Admin cannot deactivate their own account' }),
        };
      },
      '/api/v1/users': async () => ({
        ok: true,
        json: async () => [
          { id: 'admin_id_100', email: 'admin@siteintel.com', full_name: 'Rajesh Admin', role: 'admin', created_at: '2026-07-24T12:00:00Z' },
        ],
      }),
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <UserManagementPage />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Rajesh Admin')).toBeInTheDocument();
    });

    const deactBtn = screen.getByTestId('deactivate-user-btn-admin_id_100');
    fireEvent.click(deactBtn);

    await waitFor(() => {
      expect(screen.getByText(/Confirm Account Deactivation/i)).toBeInTheDocument();
    });

    const confirmBtn = screen.getByTestId('confirm-deactivate-btn');
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(deactivateCalled).toBe(true);
      const errBanner = screen.getByTestId('user-deact-error-banner');
      expect(errBanner).toBeInTheDocument();
      expect(errBanner).toHaveTextContent('Admin cannot deactivate their own account');
    });

    console.log('\n[PHASE 5 FRONTEND TEST 5] UserManagementPage rendered admin self-deactivation 400 inline error banner!');
  });

  it('6. DashboardOverviewPage - Renders pending_escalations card & system_health panel', async () => {
    setupDynamicFetchMock('admin', {
      '/api/v1/dashboard/summary': async () => ({
        ok: true,
        json: async () => ({
          worker_count: 3,
          ppe_compliance_rate: 94.2,
          active_equipment_count: 2,
          total_delivery_count: 8,
          open_hazard_count: 1,
          flagged_discrepancy_count: 4,
          pending_escalations: 2,
          system_health: {
            cameras_online: 4,
            cameras_offline: 0,
            detection_pipeline_status: 'operational',
          },
        }),
      }),
      '/api/v1/deliveries/materials': async () => ({
        ok: true,
        json: async () => [],
      }),
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <DashboardOverviewPage />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('pending-escalations-card')).toBeInTheDocument();
      expect(screen.getByTestId('pending-escalations-count')).toHaveTextContent('2');
      expect(screen.getByTestId('system-health-panel')).toBeInTheDocument();
      expect(screen.getByText('operational')).toBeInTheDocument();
    });

    console.log('\n[PHASE 5 FRONTEND TEST 6] DashboardOverviewPage rendered pending_escalations card & system_health panel!');
  });
});

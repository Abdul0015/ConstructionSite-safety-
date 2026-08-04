import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './store/authContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardShell } from './components/DashboardShell';
import { LoginPage } from './pages/LoginPage';
import { DashboardOverviewPage } from './pages/DashboardOverviewPage';
import { ViolationsPage } from './pages/ViolationsPage';
import { HazardReportPage } from './pages/HazardReportPage';
import { DeliveryLogPage } from './pages/DeliveryLogPage';
import { DiscrepancyPage } from './pages/DiscrepancyPage';
import { ZoneManagementPage } from './pages/ZoneManagementPage';
import { EquipmentPage } from './pages/EquipmentPage';
import { UserManagementPage } from './pages/UserManagementPage';

const DefaultRedirect: React.FC = () => {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === 'worker') return <Navigate to="/hazards" replace />;
  return <Navigate to="/dashboard" replace />;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          {/* Public Auth Route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Routes (All Authenticated Roles) */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="/hazards"
              element={
                <DashboardShell>
                  <HazardReportPage />
                </DashboardShell>
              }
            />
          </Route>

          {/* Protected Routes (Admin & Supervisor Only) */}
          <Route element={<ProtectedRoute allowedRoles={['admin', 'supervisor']} />}>
            <Route
              path="/dashboard"
              element={
                <DashboardShell>
                  <DashboardOverviewPage />
                </DashboardShell>
              }
            />
            <Route
              path="/violations"
              element={
                <DashboardShell>
                  <ViolationsPage />
                </DashboardShell>
              }
            />
            <Route
              path="/deliveries"
              element={
                <DashboardShell>
                  <DeliveryLogPage />
                </DashboardShell>
              }
            />
            <Route
              path="/equipment"
              element={
                <DashboardShell>
                  <EquipmentPage />
                </DashboardShell>
              }
            />
            <Route
              path="/zones"
              element={
                <DashboardShell>
                  <ZoneManagementPage />
                </DashboardShell>
              }
            />
          </Route>

          {/* Protected Routes (Admin Only) */}
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route
              path="/discrepancies"
              element={
                <DashboardShell>
                  <DiscrepancyPage />
                </DashboardShell>
              }
            />
            <Route
              path="/users"
              element={
                <DashboardShell>
                  <UserManagementPage />
                </DashboardShell>
              }
            />
          </Route>

          {/* Default Role-Aware Redirect */}
          <Route path="*" element={<DefaultRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

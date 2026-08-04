import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../store/authContext';
import { ShieldAlert } from 'lucide-react';

interface ProtectedRouteProps {
  allowedRoles?: ('admin' | 'supervisor' | 'worker')[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="w-5 h-5 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></span>
          <span>Loading session...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6">
        <div className="bg-slate-800 border border-rose-500/30 rounded-2xl p-8 max-w-md text-center">
          <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-100">Access Denied (403)</h2>
          <p className="text-sm text-slate-400 mt-2">
            Your role (<span className="text-rose-400 font-semibold">{user.role}</span>) does not have authorization to view this area.
          </p>
          <div className="mt-6 text-xs text-slate-500">
            Note: Security policy enforced server-side.
          </div>
        </div>
      </div>
    );
  }

  return <Outlet />;
};

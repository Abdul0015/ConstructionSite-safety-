import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../store/authContext';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  AlertTriangle, 
  Truck, 
  ShieldAlert, 
  FilePlus, 
  LogOut, 
  User,
  MapPin,
  HardHat,
  Users
} from 'lucide-react';

export const DashboardShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Overview', path: '/dashboard', icon: LayoutDashboard, roles: ['admin', 'supervisor'] },
    { label: 'PPE & Violations', path: '/violations', icon: ShieldCheck, roles: ['admin', 'supervisor'] },
    { label: 'Delivery & Materials', path: '/deliveries', icon: Truck, roles: ['supervisor', 'admin'] },
    { label: 'Fraud Discrepancies', path: '/discrepancies', icon: ShieldAlert, roles: ['admin'] },
    { label: 'Restricted Zones', path: '/zones', icon: MapPin, roles: ['admin', 'supervisor'] },
    { label: 'Equipment Tracking', path: '/equipment', icon: HardHat, roles: ['admin', 'supervisor'] },
    { label: 'User Management', path: '/users', icon: Users, roles: ['admin'] },
    { label: 'Report Hazard', path: '/hazards', icon: FilePlus, roles: ['worker', 'supervisor', 'admin'] },
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-slate-800/80 border-r border-slate-800 flex flex-col shrink-0">
        <div className="p-6 flex items-center space-x-3 border-b border-slate-800">
          <ShieldCheck className="w-7 h-7 text-sky-400" />
          <div>
            <h1 className="font-bold text-base text-slate-100 leading-tight">Site Intelligence</h1>
            <p className="text-xs text-sky-400">AI Platform v1.1</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isAllowed = user && item.roles.includes(user.role);
            if (!isAllowed) return null;

            const isActive = location.pathname === item.path;
            const Icon = item.icon;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User Profile Info Footer */}
        {user && (
          <div className="p-4 border-t border-slate-800 bg-slate-800/40">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 truncate">
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sky-400 font-bold text-xs shrink-0">
                  <User className="w-4 h-4" />
                </div>
                <div className="truncate">
                  <p className="text-sm font-semibold text-slate-200 truncate">{user.full_name}</p>
                  <span className={`inline-block text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                    user.role === 'admin' 
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                      : user.role === 'supervisor'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}>
                    {user.role}
                  </span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                title="Log out"
                className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-10 overflow-y-auto">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { useAuth } from '../store/authContext';
import { User, fetchUsersApi, createUserApi, deactivateUserApi } from '../services/api/usersApi';
import { Users, UserPlus, UserX, AlertCircle, CheckCircle2, Shield } from 'lucide-react';

export const UserManagementPage: React.FC = () => {
  const { token, user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Add User Modal State
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [email, setEmail] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [role, setRole] = useState<'admin' | 'supervisor' | 'worker'>('worker');

  // Deactivate Confirmation Modal State
  const [deactUserTarget, setDeactUserTarget] = useState<User | null>(null);

  // Error / Success Banners
  const [pageError, setPageError] = useState<string | null>(null);
  const [modalError, setModalError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetchUsersApi(token)
      .then((data) => setUsers(Array.isArray(data) ? data : []))
      .catch((err) => setPageError(err.message || 'Failed to load user list.'))
      .finally(() => setLoading(false));
  }, [token]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setModalError(null);
    setSuccessMsg(null);
    setSubmitting(true);

    try {
      const newUser = await createUserApi(token, { email, full_name: fullName, password, role });
      setUsers([newUser, ...users]);
      setSuccessMsg(`User account '${newUser.email}' created successfully!`);
      setShowAddModal(false);
      setEmail('');
      setFullName('');
      setPassword('');
    } catch (err: any) {
      setModalError(err.message || 'Failed to create user.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmDeactivate = async () => {
    if (!token || !deactUserTarget) return;
    setPageError(null);
    setSuccessMsg(null);
    setSubmitting(true);

    try {
      await deactivateUserApi(token, deactUserTarget.id);
      setUsers((prev) => prev.filter((u) => u.id !== deactUserTarget.id));
      setSuccessMsg(`User account '${deactUserTarget.email}' deactivated.`);
      setDeactUserTarget(null);
    } catch (err: any) {
      const errorMsg = err.detail || err.message || 'Failed to deactivate user.';
      setPageError(errorMsg);
      setDeactUserTarget(null);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">User Account Management</h2>
          <p className="text-sm text-slate-400 mt-1">Admin oversight and role-based access control management</p>
        </div>

        <button
          onClick={() => {
            setModalError(null);
            setShowAddModal(true);
          }}
          className="px-4 py-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-xl text-sm transition flex items-center space-x-2"
        >
          <UserPlus className="w-4 h-4" />
          <span>Add New User</span>
        </button>
      </div>

      {pageError && (
        <div data-testid="user-deact-error-banner" className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center space-x-3 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{pageError}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-3 text-emerald-400 text-sm">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading user accounts...</div>
        ) : users.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <Users className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p>No user accounts found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs font-semibold uppercase text-slate-400 border-b border-slate-700/60">
                <tr>
                  <th className="px-6 py-4">Full Name</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4">Role</th>
                  <th className="px-6 py-4">Created At</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/40">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/60 transition">
                    <td className="px-6 py-4 font-bold text-slate-100">{u.full_name}</td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-300">{u.email}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                        u.role === 'admin'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : u.role === 'supervisor'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        <Shield className="w-3 h-3 mr-1" />
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        data-testid={`deactivate-user-btn-${u.id}`}
                        onClick={() => setDeactUserTarget(u)}
                        className="px-3 py-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 rounded-lg text-xs font-semibold transition inline-flex items-center space-x-1"
                      >
                        <UserX className="w-3.5 h-3.5 mr-1" />
                        Deactivate
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
              <UserPlus className="w-5 h-5 text-sky-400" />
              <span>Create User Account</span>
            </h3>

            {modalError && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs">
                {modalError}
              </div>
            )}

            <form onSubmit={handleCreateUser} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Account Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as any)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                >
                  <option value="worker">Worker</option>
                  <option value="supervisor">Supervisor</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl text-sm font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-xl text-sm transition disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Deactivate Confirmation Modal */}
      {deactUserTarget && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-rose-400 flex items-center space-x-2">
              <UserX className="w-5 h-5" />
              <span>Confirm Account Deactivation</span>
            </h3>

            <p className="text-sm text-slate-300">
              Are you sure you want to deactivate user account <strong className="text-slate-100 font-mono">{deactUserTarget.email}</strong>?
            </p>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setDeactUserTarget(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl text-sm font-medium transition"
              >
                Cancel
              </button>
              <button
                data-testid="confirm-deactivate-btn"
                onClick={handleConfirmDeactivate}
                disabled={submitting}
                className="px-4 py-2 bg-rose-500 hover:bg-rose-400 text-white font-bold rounded-xl text-sm transition disabled:opacity-50"
              >
                {submitting ? 'Deactivating...' : 'Confirm Deactivation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

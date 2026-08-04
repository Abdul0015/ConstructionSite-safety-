import React, { useEffect, useState } from 'react';
import { useAuth } from '../store/authContext';
import { DeliveryLog, fetchDiscrepanciesApi, resolveDiscrepancyApi } from '../services/api/deliveriesApi';
import { ShieldAlert, AlertCircle, CheckCircle, Search } from 'lucide-react';

export const DiscrepancyPage: React.FC = () => {
  const { token, user } = useAuth();
  const [discrepancies, setDiscrepancies] = useState<DeliveryLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [resolveNotes, setResolveNotes] = useState<{ [id: string]: string }>({});
  const [resolveLoading, setResolveLoading] = useState<{ [id: string]: boolean }>({});

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetchDiscrepanciesApi(token)
      .then((data) => setDiscrepancies(Array.isArray(data) ? data : []))
      .catch((err) => setErrorMsg(err.message || 'Failed to load discrepancies.'))
      .finally(() => setLoading(false));
  }, [token]);

  const handleResolve = async (id: string, action: 'resolve' | 'flag_for_investigation') => {
    if (!token) return;
    setResolveLoading((prev) => ({ ...prev, [id]: true }));

    try {
      const notes = resolveNotes[id] || undefined;
      const updated = await resolveDiscrepancyApi(token, id, action, notes);

      // Update state inline
      setDiscrepancies((prev) =>
        prev.map((d) => (d.id === id ? { ...d, discrepancy_resolved: true, resolved_by: updated.resolved_by, resolved_at: updated.resolved_at } : d))
      );
    } catch (err: any) {
      alert(err.message || 'Failed to resolve discrepancy');
    } finally {
      setResolveLoading((prev) => ({ ...prev, [id]: false }));
    }
  };

  const isAdmin = user && user.role === 'admin';

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-500">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Delivery Fraud & Count Discrepancies</h2>
          <p className="text-xs text-rose-400 font-semibold uppercase tracking-wider">Admin Restricted Oversight Console</p>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center space-x-2 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading escalated delivery discrepancies...</div>
        ) : discrepancies.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p>No delivery count discrepancies flagged.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs font-semibold uppercase text-slate-400 border-b border-slate-700/60">
                <tr>
                  <th className="px-6 py-4">Logged Timestamp</th>
                  <th className="px-6 py-4">AI Count</th>
                  <th className="px-6 py-4">Supervisor Reported</th>
                  <th className="px-6 py-4">Material Details</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Resolution Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/40">
                {discrepancies.map((d) => {
                  const isResolved = d.discrepancy_resolved;
                  return (
                    <tr key={d.id} className="hover:bg-slate-800/60 transition">
                      <td className="px-6 py-4 font-mono text-xs text-slate-400">
                        {new Date(d.logged_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 font-bold text-sky-400">
                        {d.ai_vehicle_count === null || d.ai_vehicle_count === undefined ? 'Pending AI' : d.ai_vehicle_count}
                      </td>
                      <td className="px-6 py-4 font-bold text-rose-400">{d.manual_reported_count}</td>
                      <td className="px-6 py-4 text-xs">
                        <span className="font-semibold text-slate-200 uppercase">{d.material_type}</span> ({d.material_quantity} {d.quantity_unit})
                      </td>
                      <td className="px-6 py-4">
                        <span
                          data-testid={`discrepancy-status-badge-${d.id}`}
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                            isResolved
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}
                        >
                          {isResolved ? 'RESOLVED' : 'UNRESOLVED MISMATCH'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {isResolved ? (
                          <div className="text-xs text-slate-400">
                            <span className="text-emerald-400 font-semibold">• Resolved by Admin</span>
                          </div>
                        ) : isAdmin ? (
                          <div className="flex flex-col space-y-2">
                            <input
                              type="text"
                              placeholder="Audit notes..."
                              value={resolveNotes[d.id] || ''}
                              onChange={(e) => setResolveNotes({ ...resolveNotes, [d.id]: e.target.value })}
                              className="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-sky-500"
                            />
                            <div className="flex items-center space-x-2">
                              <button
                                data-testid={`resolve-btn-${d.id}`}
                                onClick={() => handleResolve(d.id, 'resolve')}
                                disabled={resolveLoading[d.id]}
                                className="px-3 py-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-lg text-xs transition disabled:opacity-50 flex items-center space-x-1"
                              >
                                <CheckCircle className="w-3.5 h-3.5 mr-1" />
                                Resolve
                              </button>
                              <button
                                data-testid={`flag-btn-${d.id}`}
                                onClick={() => handleResolve(d.id, 'flag_for_investigation')}
                                disabled={resolveLoading[d.id]}
                                className="px-3 py-1 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs transition disabled:opacity-50 flex items-center space-x-1"
                              >
                                <Search className="w-3.5 h-3.5 mr-1" />
                                Flag Investigation
                              </button>
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-500">Admin Action Only</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

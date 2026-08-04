import React, { useEffect, useState } from 'react';
import { useAuth } from '../store/authContext';
import { Equipment, fetchEquipmentApi } from '../services/api/equipmentApi';
import { HardHat, Activity, Clock, MapPin } from 'lucide-react';

export const EquipmentPage: React.FC = () => {
  const { token } = useAuth();
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetchEquipmentApi(token)
      .then((data) => setEquipmentList(Array.isArray(data) ? data : []))
      .catch(() => setEquipmentList([]))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Heavy Machinery & Equipment Tracking</h2>
          <p className="text-sm text-slate-400 mt-1">Live equipment status and idle duration log reading from backend service</p>
        </div>
      </div>

      <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading equipment status...</div>
        ) : equipmentList.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <HardHat className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p>No equipment currently recorded in database.</p>
            <p className="text-xs text-slate-600 mt-1">(Reads live from equipment table; active AI detection pipeline feeds update rows.)</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs font-semibold uppercase text-slate-400 border-b border-slate-700/60">
                <tr>
                  <th className="px-6 py-4">Equipment Tag / Identifier</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Location Description</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Idle Duration</th>
                  <th className="px-6 py-4">Last Update</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/40">
                {equipmentList.map((eq) => (
                  <tr key={eq.id} className="hover:bg-slate-800/60 transition">
                    <td className="px-6 py-4 font-bold text-sky-400 font-mono">
                      {eq.identifier || `TAG-${eq.id.substring(0, 6)}`}
                    </td>
                    <td className="px-6 py-4 font-semibold capitalize text-slate-200">{eq.equipment_type}</td>
                    <td className="px-6 py-4 text-xs text-slate-400 flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span>{eq.location_description || 'General Site'}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                        eq.status === 'active'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        <Activity className="w-3.5 h-3.5 mr-1" />
                        {eq.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-amber-400">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3.5 h-3.5 shrink-0" />
                        <span>{eq.idle_minutes} min</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">
                      {new Date(eq.updated_at || eq.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

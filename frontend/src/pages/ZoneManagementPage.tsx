import React, { useEffect, useState } from 'react';
import { useAuth } from '../store/authContext';
import { Zone, fetchZonesApi, createZoneApi } from '../services/api/zonesApi';
import { MapPin, Plus, AlertCircle, CheckCircle2 } from 'lucide-react';

export const ZoneManagementPage: React.FC = () => {
  const { token, user } = useAuth();
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [name, setName] = useState<string>('');
  const [zoneType, setZoneType] = useState<string>('excavation');
  const [polygonInput, setPolygonInput] = useState<string>('[{"x": 100, "y": 200}, {"x": 300, "y": 200}, {"x": 300, "y": 400}, {"x": 100, "y": 400}]');
  const [cameraId, setCameraId] = useState<string>('cam_zone_01');
  const [ppeReqs, setPpeReqs] = useState<string>('helmet, harness');
  
  const [formError, setFormError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetchZonesApi(token)
      .then((data) => setZones(Array.isArray(data) ? data : []))
      .catch(() => setZones([]))
      .finally(() => setLoading(false));
  }, [token]);

  const handleCreateZone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setFormError(null);
    setSuccessMsg(null);
    setSubmitting(true);

    try {
      let parsedCoords: any;
      try {
        parsedCoords = JSON.parse(polygonInput);
      } catch (err) {
        setFormError('Invalid JSON format for polygon coordinates. Please enter a valid JSON array of points e.g. [{"x": 100, "y": 200}, ...]');
        setSubmitting(false);
        return;
      }

      const ppeList = ppeReqs.split(',').map((s) => s.trim()).filter(Boolean);

      const createdZone = await createZoneApi(token, {
        name,
        zone_type: zoneType,
        polygon_coords: parsedCoords,
        camera_id: cameraId || undefined,
        ppe_requirements: ppeList,
        is_active: true,
      });

      setZones([createdZone, ...zones]);
      setSuccessMsg(`Restricted zone '${createdZone.name}' configured successfully!`);
      setName('');
    } catch (err: any) {
      setFormError(err.message || 'Failed to create zone.');
    } finally {
      setSubmitting(false);
    }
  };

  const isAdmin = user && user.role === 'admin';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Restricted Zone Management</h2>
          <p className="text-sm text-slate-400 mt-1">Define polygon geofence areas and camera-bound PPE policies</p>
        </div>
      </div>

      {isAdmin && (
        <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
            <Plus className="w-5 h-5 text-sky-400" />
            <span>Configure New Restricted Zone</span>
          </h3>

          {formError && (
            <div data-testid="zone-form-error" className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center space-x-3 text-rose-400 text-sm">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-3 text-emerald-400 text-sm">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleCreateZone} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Zone Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Crane Heavy Lift Sector"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Zone Type</label>
              <select
                value={zoneType}
                onChange={(e) => setZoneType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="excavation">Excavation</option>
                <option value="crane">Crane Operation</option>
                <option value="high_voltage">High Voltage</option>
                <option value="chemical_storage">Chemical Storage</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Polygon Coordinates (JSON Array)</label>
              <textarea
                rows={2}
                required
                value={polygonInput}
                onChange={(e) => setPolygonInput(e.target.value)}
                placeholder='[{"x": 100, "y": 200}, {"x": 300, "y": 200}, {"x": 300, "y": 400}, {"x": 100, "y": 400}]'
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Camera Stream ID</label>
              <input
                type="text"
                value={cameraId}
                onChange={(e) => setCameraId(e.target.value)}
                placeholder="cam_zone_01"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Required PPE (comma-separated)</label>
              <input
                type="text"
                value={ppeReqs}
                onChange={(e) => setPpeReqs(e.target.value)}
                placeholder="helmet, harness, vest"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                disabled={submitting}
                className="px-5 py-2.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-xl text-sm transition disabled:opacity-50"
              >
                {submitting ? 'Validating & Saving...' : 'Save Zone Policy'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading zones...</div>
        ) : zones.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <MapPin className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p>No restricted zones defined.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs font-semibold uppercase text-slate-400 border-b border-slate-700/60">
                <tr>
                  <th className="px-6 py-4">Zone Name</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Camera ID</th>
                  <th className="px-6 py-4">Polygon Coordinates</th>
                  <th className="px-6 py-4">PPE Requirements</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/40">
                {zones.map((z) => (
                  <tr key={z.id} className="hover:bg-slate-800/60 transition">
                    <td className="px-6 py-4 font-bold text-slate-100">{z.name}</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                        {z.zone_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">{z.camera_id || 'N/A'}</td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400 max-w-xs truncate">{z.polygon_coords}</td>
                    <td className="px-6 py-4 text-xs text-amber-400 font-semibold">{z.ppe_requirements || 'Standard PPE'}</td>
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

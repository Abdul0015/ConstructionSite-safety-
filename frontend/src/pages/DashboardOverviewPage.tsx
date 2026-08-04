import React, { useEffect, useState } from 'react';
import { useAuth } from '../store/authContext';
import { DashboardSummary, fetchDashboardSummaryApi } from '../services/api/dashboardApi';
import { MaterialInflowSummary, fetchMaterialsSummaryApi } from '../services/api/deliveriesApi';
import { 
  Users, 
  ShieldCheck, 
  Activity, 
  Truck, 
  AlertTriangle, 
  ShieldAlert, 
  PackageCheck,
  Video,
  Flame,
  X,
  Play,
  CheckCircle2,
  Tv
} from 'lucide-react';

const CAMERA_STREAMS = [
  {
    id: 'cam-01',
    name: 'Main Entry Gate 1 (Online Feed)',
    location: 'Gate 01 - North Entrance',
    status: 'ONLINE',
    fps: 30,
    res: '1080p',
    clipUrl: '/storage/demo_clips/demo_compliant.mp4',
    type: 'PPE Compliance Monitor'
  },
  {
    id: 'cam-02',
    name: 'Zone Alpha Excavation Area (Online Feed)',
    location: 'Sector 4 Restricted Zone',
    status: 'ONLINE',
    fps: 30,
    res: '1080p',
    clipUrl: '/storage/demo_clips/demo_violation.mp4',
    type: 'Helmet & Zone Breach Monitor'
  },
  {
    id: 'cam-03',
    name: 'Perimeter Night Surveillance (Low Light)',
    location: 'West Fence Line',
    status: 'ONLINE',
    fps: 24,
    res: '720p IR',
    clipUrl: '/storage/demo_clips/demo_night_lowlight.mp4',
    type: 'Infrared Night Vision'
  },
  {
    id: 'cam-04',
    name: 'Vehicle & Logistics Scale Cam',
    location: 'Gate 01 - Weighbridge',
    status: 'ONLINE',
    fps: 30,
    res: '1080p',
    clipUrl: '/storage/demo_clips/demo_vehicle_entry.mp4',
    type: 'Vehicle Counting AI'
  }
];

export const DashboardOverviewPage: React.FC = () => {
  const { token } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [materials, setMaterials] = useState<MaterialInflowSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedStream, setSelectedStream] = useState<typeof CAMERA_STREAMS[0] | null>(null);

  useEffect(() => {
    if (!token) return;

    Promise.all([
      fetchDashboardSummaryApi(token),
      fetchMaterialsSummaryApi(token).catch(() => [])
    ])
      .then(([summaryData, materialsData]) => {
        setSummary(summaryData);
        setMaterials(Array.isArray(materialsData) ? materialsData : []);
      })
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center space-x-3 text-slate-400 py-12">
        <span className="w-5 h-5 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></span>
        <span>Loading dashboard KPIs...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">Site Safety & Activity Overview</h2>
        <p className="text-sm text-slate-400 mt-1">Real-time aggregate site intelligence metrics</p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">PPE Compliance Rate</p>
            <p className="text-3xl font-extrabold text-emerald-400 mt-2">
              {summary?.ppe_compliance_rate === null || summary?.ppe_compliance_rate === undefined ? 'N/A' : `${summary.ppe_compliance_rate}%`}
            </p>
          </div>
          <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Active Workers</p>
            <p className="text-3xl font-extrabold text-sky-400 mt-2">{summary?.worker_count ?? 0}</p>
          </div>
          <div className="w-12 h-12 bg-sky-500/10 border border-sky-500/20 rounded-xl flex items-center justify-center text-sky-400">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Active Equipment</p>
            <p className="text-3xl font-extrabold text-indigo-400 mt-2">{summary?.active_equipment_count ?? 0}</p>
          </div>
          <div className="w-12 h-12 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex items-center justify-center text-indigo-400">
            <Activity className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Deliveries Logged</p>
            <p className="text-3xl font-extrabold text-amber-400 mt-2">{summary?.total_delivery_count ?? 0}</p>
          </div>
          <div className="w-12 h-12 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center justify-center text-amber-400">
            <Truck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Open Hazard Reports</p>
            <p className="text-3xl font-extrabold text-orange-400 mt-2">{summary?.open_hazard_count ?? 0}</p>
          </div>
          <div className="w-12 h-12 bg-orange-500/10 border border-orange-500/20 rounded-xl flex items-center justify-center text-orange-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">All-Time Flagged Mismatches</p>
            <p className="text-3xl font-extrabold text-rose-400 mt-2">{summary?.flagged_discrepancy_count ?? 0}</p>
          </div>
          <div className="w-12 h-12 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center justify-center text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        {/* Pending Escalations KPI Card */}
        <div data-testid="pending-escalations-card" className="bg-slate-800/80 border border-rose-500/40 p-6 rounded-2xl flex items-center justify-between shadow-lg">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-rose-400">Pending Escalations</p>
            <p data-testid="pending-escalations-count" className="text-3xl font-extrabold text-rose-500 mt-2">
              {summary?.pending_escalations ?? 0}
            </p>
            <p className="text-[10px] text-slate-400 mt-1">Unresolved count mismatches</p>
          </div>
          <div className="w-12 h-12 bg-rose-500/20 border border-rose-500/40 rounded-xl flex items-center justify-center text-rose-400 animate-pulse">
            <Flame className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* System Health Indicator Panel */}
      <div data-testid="system-health-panel" className="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Video className="w-6 h-6 text-sky-400" />
            <h3 className="text-lg font-bold text-slate-100">Camera System Health & Vision Pipeline</h3>
          </div>
          <button 
            onClick={() => setSelectedStream(CAMERA_STREAMS[0])}
            className="flex items-center space-x-2 px-3 py-1.5 bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 text-xs font-semibold rounded-xl transition"
          >
            <Tv className="w-4 h-4" />
            <span>Open Camera Stream Viewer</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            onClick={() => setSelectedStream(CAMERA_STREAMS[0])}
            className="bg-slate-900/60 border border-slate-700/50 hover:border-emerald-500/50 p-4 rounded-xl flex items-center justify-between text-left transition group cursor-pointer"
          >
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase group-hover:text-emerald-400 transition">Cameras Online (Click to View)</p>
              <p className="text-2xl font-bold text-emerald-400 mt-1">{summary?.system_health?.cameras_online ?? 0}</p>
            </div>
            <span className="w-3 h-3 rounded-full bg-emerald-400 animate-ping"></span>
          </button>

          <button 
            onClick={() => setSelectedStream(CAMERA_STREAMS[2])}
            className="bg-slate-900/60 border border-slate-700/50 hover:border-slate-500 p-4 rounded-xl flex items-center justify-between text-left transition group cursor-pointer"
          >
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase group-hover:text-slate-200 transition">Cameras Offline (IR Standby)</p>
              <p className="text-2xl font-bold text-slate-400 mt-1">{summary?.system_health?.cameras_offline ?? 0}</p>
            </div>
            <span className="w-3 h-3 rounded-full bg-slate-600"></span>
          </button>

          <button 
            onClick={() => setSelectedStream(CAMERA_STREAMS[1])}
            className="bg-slate-900/60 border border-slate-700/50 hover:border-sky-500/50 p-4 rounded-xl flex items-center justify-between text-left transition group cursor-pointer"
          >
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase group-hover:text-sky-400 transition">Vision Service Pipeline</p>
              <span className="inline-block mt-1 px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold uppercase rounded-full">
                {summary?.system_health?.detection_pipeline_status || 'Operational'}
              </span>
            </div>
            <Play className="w-5 h-5 text-sky-400 opacity-60 group-hover:opacity-100 transition" />
          </button>
        </div>
      </div>

      {/* Interactive Camera Stream Player Modal */}
      {selectedStream && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full p-6 shadow-2xl relative space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full bg-emerald-400 animate-ping"></div>
                <div>
                  <h3 className="text-lg font-bold text-slate-100">{selectedStream.name}</h3>
                  <p className="text-xs text-slate-400">{selectedStream.location} • {selectedStream.type}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedStream(null)}
                className="p-2 text-slate-400 hover:text-slate-100 bg-slate-800 rounded-xl transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Video Player */}
            <div className="relative bg-black rounded-xl overflow-hidden aspect-video border border-slate-800 flex items-center justify-center group">
              <video
                key={selectedStream.id}
                src={selectedStream.clipUrl}
                autoPlay
                loop
                muted
                controls
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 left-4 bg-slate-950/80 border border-slate-700 px-3 py-1.5 rounded-lg flex items-center space-x-2 text-xs font-mono text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>REC LIVE • {selectedStream.res} • {selectedStream.fps} FPS</span>
              </div>
            </div>

            {/* Stream Selector Tabs */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {CAMERA_STREAMS.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSelectedStream(s)}
                  className={`p-3 rounded-xl border text-left text-xs transition ${
                    selectedStream.id === s.id
                      ? 'bg-sky-500/10 border-sky-500/50 text-sky-400 font-bold'
                      : 'bg-slate-800/60 border-slate-700/50 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <p className="truncate font-semibold">{s.name}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">{s.res} • {s.status}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Material Inflow Log Summary Card */}
      <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <PackageCheck className="w-6 h-6 text-sky-400" />
          <h3 className="text-lg font-bold text-slate-100">Material Inflow Log Summary</h3>
        </div>

        {materials.length === 0 ? (
          <p className="text-sm text-slate-500">No material inflow records logged yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {materials.map((m) => (
              <div key={m.material_type} className="bg-slate-900/60 border border-slate-700/50 p-4 rounded-xl">
                <span className="text-xs font-bold uppercase text-slate-400">{m.material_type}</span>
                <p className="text-xl font-extrabold text-slate-100 mt-1">
                  {m.total_quantity} <span className="text-xs font-medium text-slate-400">{m.quantity_unit}</span>
                </p>
                <p className="text-xs text-slate-500 mt-1">{m.delivery_count} deliveries</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

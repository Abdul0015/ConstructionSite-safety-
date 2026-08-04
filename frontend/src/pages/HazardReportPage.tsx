import React, { useState, useEffect } from 'react';
import { useAuth } from '../store/authContext';
import { HazardReport, createHazardReportApi, fetchHazardReportsApi } from '../services/api/hazardsApi';
import { AlertTriangle, Upload, CheckCircle2, AlertCircle } from 'lucide-react';

export const HazardReportPage: React.FC = () => {
  const { token } = useAuth();
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [category, setCategory] = useState('other');
  const [file, setFile] = useState<File | null>(null);
  
  const [reports, setReports] = useState<HazardReport[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    fetchHazardReportsApi(token)
      .then(setReports)
      .catch(() => setReports([]));
  }, [token]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (selected.size > 5 * 1024 * 1024) {
      setErrorMsg('File size exceeds maximum 5MB limit.');
      setFile(null);
      return;
    }

    if (!['image/jpeg', 'image/png'].includes(selected.type)) {
      setErrorMsg('Only JPEG and PNG image files are permitted.');
      setFile(null);
      return;
    }

    setErrorMsg(null);
    setFile(selected);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setSubmitting(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('description', description);
    formData.append('location', location);
    formData.append('category', category);
    if (file) {
      formData.append('file', file);
    }

    try {
      const newReport = await createHazardReportApi(token, formData);
      setSuccessMsg('Hazard report submitted and logged successfully!');
      setDescription('');
      setLocation('');
      setCategory('other');
      setFile(null);
      setReports((prev) => [newReport, ...prev]);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit report.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Hazard Report Form */}
      <div className="lg:col-span-1 bg-slate-800/80 border border-slate-700/60 rounded-2xl p-6 shadow-xl h-fit">
        <div className="flex items-center space-x-3 mb-6">
          <AlertTriangle className="w-6 h-6 text-orange-400" />
          <h2 className="text-xl font-bold text-slate-100">Submit Hazard Report</h2>
        </div>

        {successMsg && (
          <div className="mb-4 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-2 text-emerald-400 text-sm">
            <CheckCircle2 className="w-5 h-5 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {errorMsg && (
          <div className="mb-4 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center space-x-2 text-rose-400 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Hazard Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
            >
              <option value="fire_risk">Fire Risk</option>
              <option value="unsafe_wiring">Unsafe Wiring / Electrical</option>
              <option value="water_leakage">Water Leakage</option>
              <option value="scaffold_damage">Scaffold Damage</option>
              <option value="structural_cracks">Structural Cracks</option>
              <option value="other">Other Safety Hazard</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Specific Location
            </label>
            <input
              type="text"
              required
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Zone B Trench Near Pump 2"
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Detailed Description
            </label>
            <textarea
              required
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the unsafe condition observed..."
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Photo Attachment (Optional, Max 5MB)
            </label>
            <div className="border-2 border-dashed border-slate-700 rounded-xl p-4 text-center hover:border-slate-600 transition">
              <Upload className="w-6 h-6 text-slate-500 mx-auto mb-2" />
              <input
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleFileChange}
                className="hidden"
                id="file-input"
              />
              <label htmlFor="file-input" className="cursor-pointer text-xs text-sky-400 hover:text-sky-300 font-semibold">
                {file ? file.name : 'Click to select JPEG or PNG photo'}
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-slate-950 font-bold py-3 rounded-xl transition shadow-lg shadow-orange-500/20 disabled:opacity-50 text-sm"
          >
            {submitting ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>
      </div>

      {/* Submitted Hazard Reports Feed */}
      <div className="lg:col-span-2 space-y-4">
        <h3 className="text-lg font-bold text-slate-100">Logged Safety Hazard Feed</h3>
        {reports.length === 0 ? (
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-8 text-center text-slate-500">
            No hazard reports logged yet.
          </div>
        ) : (
          <div className="space-y-4">
            {reports.map((r) => (
              <div key={r.id} className="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-5 flex flex-col sm:flex-row justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 rounded-md bg-orange-500/10 text-orange-400 border border-orange-500/20 text-xs font-bold uppercase">
                      {r.category}
                    </span>
                    <span className="text-xs font-mono text-slate-500">{new Date(r.created_at).toLocaleString()}</span>
                  </div>
                  <h4 className="font-semibold text-slate-200 mt-2">{r.location}</h4>
                  <p className="text-sm text-slate-400 mt-1">{r.description}</p>
                </div>
                {r.image_url && (
                  <div className="shrink-0">
                    <a href={r.image_url} target="_blank" rel="noreferrer" className="text-xs text-sky-400 underline">
                      Attachment Photo
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

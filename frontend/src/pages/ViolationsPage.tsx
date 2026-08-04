import React, { useEffect, useState } from 'react';
import { useAuth } from '../store/authContext';
import { Violation, fetchViolationsApi, acknowledgeViolationApi, uploadVideoApi } from '../services/api/violationsApi';
import { ShieldCheck, Filter, AlertTriangle, CheckCircle, Clock, Upload, FileVideo, Sparkles, UploadCloud } from 'lucide-react';

export const ViolationsPage: React.FC = () => {
  const { token, user } = useAuth();
  const [violations, setViolations] = useState<Violation[]>([]);
  const [filterType, setFilterType] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [ackNotes, setAckNotes] = useState<{ [id: string]: string }>({});
  const [ackErrors, setAckErrors] = useState<{ [id: string]: string }>({});
  const [ackLoading, setAckLoading] = useState<{ [id: string]: boolean }>({});

  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetchViolationsApi(token, { violation_type: filterType || undefined })
      .then((data) => setViolations(data))
      .catch(() => setViolations([]))
      .finally(() => setLoading(false));
  }, [token, filterType]);

  const handleAcknowledge = async (id: string) => {
    if (!token) return;
    setAckErrors((prev) => ({ ...prev, [id]: '' }));
    setAckLoading((prev) => ({ ...prev, [id]: true }));

    try {
      const notes = ackNotes[id] || undefined;
      const updatedViolation = await acknowledgeViolationApi(token, id, notes);

      setViolations((prev) =>
        prev.map((v) => (v.id === id ? { ...v, status: 'acknowledged', acknowledged_by: updatedViolation.acknowledged_by, acknowledged_at: updatedViolation.acknowledged_at, notes: updatedViolation.notes } : v))
      );
    } catch (err: any) {
      const errorMsg = err.detail || err.message || 'Failed to acknowledge violation.';
      setAckErrors((prev) => ({ ...prev, [id]: errorMsg }));
    } finally {
      setAckLoading((prev) => ({ ...prev, [id]: false }));
    }
  };

  const handleVideoUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !videoFile) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const res = await uploadVideoApi(token, videoFile);
      setUploadSuccess(`Success! AI Vision Pipeline analyzed '${videoFile.name}'. Logged ${res.violations_detected} new violation event.`);
      setVideoFile(null);
      // Refresh list
      const freshData = await fetchViolationsApi(token, { violation_type: filterType || undefined });
      setViolations(freshData);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to process video file.');
    } finally {
      setUploading(false);
    }
  };

  const isSupervisorOrAdmin = user && (user.role === 'admin' || user.role === 'supervisor');

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">PPE & Restricted Zone Violations</h2>
          <p className="text-sm text-slate-400 mt-1">Audit log of real-time camera detection events</p>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-3 py-2 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Violations</option>
            <option value="ppe_missing">PPE Missing</option>
            <option value="restricted_zone_entry">Restricted Zone Entry</option>
          </select>
        </div>
      </div>

      {/* Video File Upload & AI Pipeline Ingestion Card (Admin & Supervisor) */}
      {isSupervisorOrAdmin && (
        <div className="bg-slate-800/90 border border-sky-500/30 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                <FileVideo className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100">Upload Site Video for AI Analysis</h3>
                <p className="text-xs text-slate-400">Ingest .mp4, .avi, or .mov site video clips into YOLOv8 vision pipeline</p>
              </div>
            </div>
            <span className="hidden sm:inline-flex items-center space-x-1.5 px-3 py-1 bg-sky-500/10 text-sky-400 border border-sky-500/20 text-xs font-semibold rounded-full">
              <Sparkles className="w-3.5 h-3.5" />
              <span>YOLOv8 Autonomous Analysis</span>
            </span>
          </div>

          {uploadSuccess && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl flex items-center space-x-2 font-medium">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{uploadSuccess}</span>
            </div>
          )}

          {uploadError && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl flex items-center space-x-2 font-medium">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <form onSubmit={handleVideoUpload} className="flex flex-col sm:flex-row items-center gap-4">
            <input
              type="file"
              accept="video/mp4,video/x-msvideo,video/quicktime,video/mkv"
              onChange={(e) => setVideoFile(e.target.files ? e.target.files[0] : null)}
              className="block w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-700 file:text-slate-200 hover:file:bg-slate-600 cursor-pointer"
            />
            <button
              type="submit"
              disabled={!videoFile || uploading}
              className="w-full sm:w-auto px-5 py-2.5 bg-sky-500 hover:bg-sky-400 text-white rounded-xl text-xs font-bold transition flex items-center justify-center space-x-2 shrink-0 disabled:opacity-50"
            >
              <UploadCloud className="w-4 h-4" />
              <span>{uploading ? 'Processing AI Pipeline...' : 'Run AI Vision Pipeline'}</span>
            </button>
          </form>
        </div>
      )}

      <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading violations...</div>
        ) : violations.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p>No safety violations recorded.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs font-semibold uppercase text-slate-400 border-b border-slate-700/60">
                <tr>
                  <th className="px-6 py-4">Detected At</th>
                  <th className="px-6 py-4">Violation Type</th>
                  <th className="px-6 py-4">PPE Status</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Actions / Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/40">
                {violations.map((v) => {
                  const isAcknowledged = v.status === 'acknowledged';
                  return (
                    <tr key={v.id} className="hover:bg-slate-800/60 transition">
                      <td className="px-6 py-4 font-mono text-xs text-slate-400">
                        {new Date(v.detected_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 font-medium">
                        <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                          v.violation_type === 'ppe_missing'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          <AlertTriangle className="w-3.5 h-3.5 mr-1" />
                          {v.violation_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs">
                        {v.helmet_missing && <span className="text-rose-400 font-semibold mr-2">• Helmet Missing</span>}
                        {v.vest_missing && <span className="text-amber-400 font-semibold">• Vest Missing</span>}
                        {!v.helmet_missing && !v.vest_missing && <span className="text-slate-400">Zone Breach</span>}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          data-testid={`violation-status-badge-${v.id}`}
                          className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                            isAcknowledged
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}
                        >
                          {isAcknowledged ? (
                            <>
                              <CheckCircle className="w-3.5 h-3.5 mr-1" />
                              acknowledged
                            </>
                          ) : (
                            <>
                              <Clock className="w-3.5 h-3.5 mr-1" />
                              pending
                            </>
                          )}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {isAcknowledged ? (
                          <div className="text-xs text-slate-400">
                            <span className="font-semibold text-slate-300">Notes:</span> {v.notes || 'No notes added'}
                          </div>
                        ) : isSupervisorOrAdmin ? (
                          <div className="flex flex-col space-y-2">
                            <div className="flex items-center space-x-2">
                              <input
                                type="text"
                                placeholder="Add notes..."
                                value={ackNotes[v.id] || ''}
                                onChange={(e) => setAckNotes({ ...ackNotes, [v.id]: e.target.value })}
                                className="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-sky-500"
                              />
                              <button
                                data-testid={`acknowledge-btn-${v.id}`}
                                onClick={() => handleAcknowledge(v.id)}
                                disabled={ackLoading[v.id]}
                                className="px-3 py-1 bg-sky-500 hover:bg-sky-400 text-white rounded-lg text-xs font-semibold transition disabled:opacity-50"
                              >
                                {ackLoading[v.id] ? 'Saving...' : 'Acknowledge'}
                              </button>
                            </div>
                            {ackErrors[v.id] && (
                              <div
                                data-testid={`ack-error-${v.id}`}
                                className="text-xs text-rose-400 font-medium bg-rose-500/10 border border-rose-500/20 p-2 rounded-lg"
                              >
                                {ackErrors[v.id]}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-slate-500">Read-Only</span>
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

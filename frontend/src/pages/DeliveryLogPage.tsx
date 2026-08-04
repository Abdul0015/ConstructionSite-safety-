import React, { useState } from 'react';
import { useAuth } from '../store/authContext';
import { createDeliveryLogApi } from '../services/api/deliveriesApi';
import { Truck, CheckCircle2, AlertCircle } from 'lucide-react';

export const DeliveryLogPage: React.FC = () => {
  const { token } = useAuth();
  const [gateId, setGateId] = useState('00000000-0000-0000-0000-000000000001');
  const [manualReportedCount, setManualReportedCount] = useState<number>(1);
  const [materialType, setMaterialType] = useState('cement');
  const [materialQuantity, setMaterialQuantity] = useState<number>(50);
  const [quantityUnit, setQuantityUnit] = useState('bags');
  const [vehicleType, setVehicleType] = useState('mixer');

  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setSubmitting(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      const result = await createDeliveryLogApi(token, {
        gate_id: gateId,
        manual_reported_count: Number(manualReportedCount),
        material_type: materialType,
        material_quantity: Number(materialQuantity),
        quantity_unit: quantityUnit,
        vehicle_type: vehicleType,
      });

      if (result.discrepancy_flag) {
        setSuccessMsg(`Delivery entry logged! NOTE: Discrepancy detected (AI count vs Manual count mismatch).`);
      } else {
        setSuccessMsg(`Delivery entry logged successfully! Counts verified.`);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit delivery log.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-slate-800/80 border border-slate-700/60 rounded-2xl p-8 shadow-xl">
      <div className="flex items-center space-x-3 mb-6">
        <Truck className="w-7 h-7 text-amber-400" />
        <div>
          <h2 className="text-xl font-bold text-slate-100">Log Delivery Vehicle & Material Entry</h2>
          <p className="text-xs text-slate-400">Supervisor operational delivery arrival input form</p>
        </div>
      </div>

      {successMsg && (
        <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-2 text-emerald-400 text-sm">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center space-x-2 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Gate Selection
            </label>
            <input
              type="text"
              required
              value={gateId}
              onChange={(e) => setGateId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-xs font-mono text-slate-100 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Manual Vehicle Count Reported
            </label>
            <input
              type="number"
              min="0"
              required
              value={manualReportedCount}
              onChange={(e) => setManualReportedCount(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Material Type
            </label>
            <select
              value={materialType}
              onChange={(e) => setMaterialType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
            >
              <option value="cement">Cement</option>
              <option value="sand">Sand</option>
              <option value="bricks">Bricks</option>
              <option value="steel">Steel</option>
              <option value="pipes">Pipes</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label htmlFor="quantity-input" className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Quantity
            </label>
            <input
              id="quantity-input"
              type="number"
              step="0.01"
              min="0.01"
              required
              value={materialQuantity}
              onChange={(e) => setMaterialQuantity(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Unit
            </label>
            <select
              value={quantityUnit}
              onChange={(e) => setQuantityUnit(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
            >
              <option value="bags">Bags</option>
              <option value="tons">Tons</option>
              <option value="cubic_meters">Cubic Meters</option>
              <option value="pieces">Pieces</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
            Vehicle Type (Optional)
          </label>
          <input
            type="text"
            value={vehicleType}
            onChange={(e) => setVehicleType(e.target.value)}
            placeholder="e.g. mixer, tipper, flatbed"
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-amber-500 hover:bg-amber-600 active:bg-amber-700 text-slate-950 font-bold py-3.5 rounded-xl transition shadow-lg shadow-amber-500/20 disabled:opacity-50 text-sm"
        >
          {submitting ? 'Logging Delivery...' : 'Log Delivery & Material Entry'}
        </button>
      </form>
    </div>
  );
};

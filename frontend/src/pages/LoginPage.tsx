import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../store/authContext';
import { ShieldCheck, Lock, Mail, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const userData = await login(email, password);
      if (userData.role === 'worker') {
        navigate('/hazards');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Login failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuickFill = (roleEmail: string, rolePass: string) => {
    setEmail(roleEmail);
    setPassword(rolePass);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-800/80 border border-slate-700/80 rounded-2xl p-8 shadow-2xl backdrop-blur">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-sky-500/10 border border-sky-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <ShieldCheck className="w-8 h-8 text-sky-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Site Intelligence</h1>
          <p className="text-sm text-slate-400 mt-1">Sign in to your account</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start space-x-3 text-rose-400 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-5 h-5 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@siteintel.com"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-sky-500 hover:bg-sky-600 active:bg-sky-700 text-slate-950 font-bold py-3.5 rounded-xl transition shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center justify-center space-x-2 text-sm"
          >
            {submitting ? (
              <>
                <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-700/60">
          <p className="text-xs text-slate-400 mb-3 text-center">Quick Login Demo Accounts:</p>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickFill('admin@siteintel.com', 'AdminSecurePass123!')}
              className="px-2 py-1.5 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-slate-300 transition"
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('supervisor@siteintel.com', 'SupervisorSecurePass123!')}
              className="px-2 py-1.5 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-slate-300 transition"
            >
              Supervisor
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('worker@siteintel.com', 'WorkerSecurePass123!')}
              className="px-2 py-1.5 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-slate-300 transition"
            >
              Worker
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

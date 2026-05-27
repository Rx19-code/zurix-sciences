import React, { useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function Maintenance({ onBypass }) {
  const [showLogin, setShowLogin] = useState(false);
  const [key, setKey] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleBypass = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const r = await fetch(`${API}/api/maintenance/bypass`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ key: key.trim() }),
      });
      if (!r.ok) {
        const data = await r.json().catch(() => ({}));
        throw new Error(data.detail || 'Invalid key');
      }
      if (onBypass) onBypass();
      window.location.reload();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-purple-950 flex flex-col items-center justify-center px-4 py-12 text-white relative overflow-hidden">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }} />

      {/* Floating glow orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />

      <div className="relative z-10 max-w-lg w-full text-center" data-testid="maintenance-page">
        {/* Logo */}
        <div className="inline-flex items-center justify-center mb-8">
          <div className="text-3xl font-bold text-blue-400">Zurix Sciences</div>
        </div>

        {/* Animated icon */}
        <div className="inline-flex items-center justify-center w-20 h-20 mb-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 shadow-xl shadow-purple-500/40">
          <svg className="w-10 h-10 text-white animate-spin" style={{ animationDuration: '3s' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold mb-3 bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent">
          We&apos;ll be back soon
        </h1>
        <p className="text-lg text-blue-200 mb-2">
          Site under update
        </p>
        <p className="text-sm text-slate-400 mb-10 max-w-md mx-auto leading-relaxed">
          We&apos;re making improvements to bring you a better experience.
          The site will be back online shortly.
        </p>

        {/* Animated progress bar (decorative) */}
        <div className="w-full max-w-xs mx-auto mb-10">
          <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 rounded-full" style={{
              width: '40%',
              animation: 'maintenance-progress 2s ease-in-out infinite alternate'
            }} />
          </div>
          <style>{`@keyframes maintenance-progress { 0% { width: 20%; } 100% { width: 80%; } }`}</style>
        </div>

        {/* Admin bypass section */}
        {!showLogin ? (
          <button
            onClick={() => setShowLogin(true)}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors underline underline-offset-4"
            data-testid="show-admin-login"
          >
            Admin access
          </button>
        ) : (
          <form onSubmit={handleBypass} className="mt-2 max-w-xs mx-auto space-y-3" data-testid="admin-bypass-form">
            <input
              type="password"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="Admin bypass key"
              autoFocus
              className="w-full px-4 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              data-testid="bypass-key-input"
            />
            {error && (
              <p className="text-red-400 text-xs" data-testid="bypass-error">{error}</p>
            )}
            <div className="flex gap-2 justify-center">
              <button
                type="button"
                onClick={() => { setShowLogin(false); setKey(''); setError(''); }}
                className="text-slate-400 hover:text-white text-sm px-4 py-2"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-50"
                data-testid="bypass-submit-btn"
              >
                {submitting ? 'Verifying…' : 'Enter Site'}
              </button>
            </div>
          </form>
        )}

        {/* Footer */}
        <div className="mt-12 pt-6 border-t border-slate-800 space-y-2">
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl px-4 py-3 text-left max-w-sm mx-auto">
            <p className="text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">For urgent inquiries</p>
            <p className="text-slate-300 text-sm">
              <span className="text-slate-500">Email:</span>{' '}
              <a href="mailto:RxpeptidesHK@proton.me" className="text-blue-400 hover:text-blue-300">RxpeptidesHK@proton.me</a>
            </p>
            <p className="text-slate-300 text-sm">
              <span className="text-slate-500">Threema ID:</span>{' '}
              <span className="text-blue-400 font-mono">2D9DAD9R</span>
            </p>
          </div>
          <p className="text-[10px] text-slate-600 mt-3">
            © 2026 Zurix Sciences — Premium Research Compounds
          </p>
        </div>
      </div>
    </div>
  );
}

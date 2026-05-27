import React, { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function MaintenanceTab({ adminPassword }) {
  const [active, setActive] = useState(false);
  const [bypassed, setBypassed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [error, setError] = useState('');

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/api/maintenance/status`, { credentials: 'include' });
      const d = await r.json();
      setActive(!!d.active);
      setBypassed(!!d.bypass);
    } catch (e) {
      setError(`Failed to load status: ${e.message}`);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const toggle = async (newActive) => {
    if (!window.confirm(newActive
      ? 'Activate maintenance mode? Visitors will see the maintenance page (you can bypass with the admin key).'
      : 'Deactivate maintenance mode? Site will be fully public again.'
    )) return;
    setToggling(true);
    setError('');
    try {
      const r = await fetch(`${API_URL}/api/maintenance/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-admin-password': adminPassword },
        body: JSON.stringify({ active: newActive }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || `HTTP ${r.status}`);
      }
      const d = await r.json();
      setActive(!!d.active);
    } catch (e) {
      setError(`Failed: ${e.message}`);
    } finally {
      setToggling(false);
    }
  };

  if (loading) {
    return <div className="text-gray-400">Loading status…</div>;
  }

  return (
    <div className="space-y-6" data-testid="maintenance-tab">
      {/* Status banner */}
      <div className={`rounded-xl p-6 border-2 ${active ? 'bg-red-950/40 border-red-700' : 'bg-green-950/40 border-green-700'}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className={`w-3 h-3 rounded-full ${active ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
              <h3 className={`text-xl font-bold ${active ? 'text-red-300' : 'text-green-300'}`}>
                {active ? 'Maintenance Mode ACTIVE' : 'Site is LIVE'}
              </h3>
            </div>
            <p className="text-sm text-gray-400 ml-6">
              {active
                ? 'Visitors see the maintenance page. Only admins with the bypass key can access the site.'
                : 'The site is fully public and accepting all visitors.'}
            </p>
          </div>
          <button
            onClick={() => toggle(!active)}
            disabled={toggling}
            className={`px-6 py-3 rounded-lg font-semibold transition disabled:opacity-50 ${
              active
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-red-600 hover:bg-red-700 text-white'
            }`}
            data-testid="maintenance-toggle-btn"
          >
            {toggling ? '…' : (active ? '✓ Bring Site Live' : '🚧 Activate Maintenance')}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Admin bypass status */}
      {active && (
        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
          <h4 className="text-white font-semibold mb-2">Your admin bypass</h4>
          {bypassed ? (
            <div className="bg-green-950/40 border border-green-800 rounded-lg px-4 py-3 text-sm text-green-300">
              ✓ You have a bypass cookie. You can browse the site normally while maintenance is active.
            </div>
          ) : (
            <div className="bg-yellow-950/40 border border-yellow-800 rounded-lg px-4 py-3 text-sm text-yellow-300">
              ⚠ You don&apos;t have a bypass cookie yet. Open the site in a new tab, click &quot;Admin access&quot;, and enter your bypass key to enable bypass.
            </div>
          )}
        </div>
      )}

      {/* Info card */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
        <h4 className="text-white font-semibold mb-3">How it works</h4>
        <ul className="space-y-2 text-sm text-gray-400">
          <li><strong className="text-gray-300">1.</strong> Click <strong>&quot;Activate Maintenance&quot;</strong> to put the site under maintenance.</li>
          <li><strong className="text-gray-300">2.</strong> All visitors will see the maintenance page (no products/protocols visible).</li>
          <li><strong className="text-gray-300">3.</strong> To access the site as admin: open <code className="bg-gray-900 px-1.5 py-0.5 rounded text-blue-400">/</code>, click <strong>&quot;Admin access&quot;</strong>, enter your bypass key.</li>
          <li><strong className="text-gray-300">4.</strong> Bypass cookie lasts <strong>24 hours</strong>. After that, enter the key again.</li>
          <li><strong className="text-gray-300">5.</strong> Click <strong>&quot;Bring Site Live&quot;</strong> when ready to publish.</li>
        </ul>
      </div>

      <div className="bg-blue-950/40 border border-blue-800 rounded-xl p-4 text-sm text-blue-300">
        💡 <strong>Tip:</strong> Server-side payment processing keeps working during maintenance. Only the public site is hidden.
      </div>
    </div>
  );
}

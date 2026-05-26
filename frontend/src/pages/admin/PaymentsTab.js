import React, { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const STATUS_COLORS = {
  finished: 'bg-green-600 text-white',
  confirmed: 'bg-green-600 text-white',
  waiting: 'bg-yellow-600 text-white',
  confirming: 'bg-yellow-500 text-white',
  sending: 'bg-yellow-500 text-white',
  partially_paid: 'bg-orange-500 text-white',
  failed: 'bg-red-600 text-white',
  expired: 'bg-gray-500 text-white',
  refunded: 'bg-purple-600 text-white',
};

function StatusBadge({ status }) {
  const cls = STATUS_COLORS[status] || 'bg-gray-600 text-white';
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold uppercase ${cls}`} data-testid={`order-status-${status}`}>
      {status}
    </span>
  );
}

function KpiCard({ label, value, accent, testid }) {
  return (
    <div className={`bg-gray-800 rounded-xl p-4 border-l-4 ${accent}`} data-testid={testid}>
      <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}

export default function PaymentsTab({ adminPassword }) {
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQ, setSearchQ] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Grant access modal
  const [showGrant, setShowGrant] = useState(false);
  const [grantEmail, setGrantEmail] = useState('');
  const [grantNote, setGrantNote] = useState('');
  const [granting, setGranting] = useState(false);
  const [grantResult, setGrantResult] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/api/admin/payments/stats`, {
        headers: { 'x-admin-password': adminPassword },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setStats(await r.json());
    } catch (e) {
      setError(`Failed to load stats: ${e.message}`);
    }
  }, [adminPassword]);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.set('status', statusFilter);
      if (searchQ.trim()) params.set('q', searchQ.trim());
      const r = await fetch(`${API_URL}/api/admin/payments/orders?${params.toString()}`, {
        headers: { 'x-admin-password': adminPassword },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setOrders(data.orders || []);
      setTotal(data.total || 0);
    } catch (e) {
      setError(`Failed to load orders: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [adminPassword, statusFilter, searchQ]);

  useEffect(() => { fetchStats(); }, [fetchStats]);
  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  const downloadCsv = async () => {
    try {
      const r = await fetch(`${API_URL}/api/admin/payments/export.csv`, {
        headers: { 'x-admin-password': adminPassword },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const blob = await r.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `zurix_payments_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError(`Failed to export CSV: ${e.message}`);
    }
  };

  const submitGrant = async (e) => {
    e.preventDefault();
    setGranting(true);
    setGrantResult(null);
    try {
      const r = await fetch(`${API_URL}/api/admin/payments/grant-access`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-admin-password': adminPassword },
        body: JSON.stringify({ email: grantEmail.trim(), note: grantNote.trim() }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setGrantResult({ ok: true, message: data.already_had_access ? `${grantEmail} already had access.` : `Lifetime Access granted to ${grantEmail}. Order: ${data.order_id}` });
      setGrantEmail('');
      setGrantNote('');
      await fetchStats();
      await fetchOrders();
    } catch (err) {
      setGrantResult({ ok: false, message: err.message });
    } finally {
      setGranting(false);
    }
  };

  const fmtDate = (iso) => {
    if (!iso) return '—';
    try { return new Date(iso).toLocaleString(); } catch { return iso; }
  };

  return (
    <div className="space-y-6" data-testid="payments-tab">
      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <KpiCard label="Revenue" value={`$${stats.revenue_total.toFixed(2)}`} accent="border-green-500" testid="kpi-revenue" />
          <KpiCard label="Paid Orders" value={stats.paid_orders} accent="border-green-500" testid="kpi-paid" />
          <KpiCard label="Pending" value={stats.pending_orders} accent="border-yellow-500" testid="kpi-pending" />
          <KpiCard label="Conv. Rate" value={`${stats.conversion_rate}%`} accent="border-blue-500" testid="kpi-conversion" />
          <KpiCard label="Lifetime Users" value={stats.users_with_access} accent="border-purple-500" testid="kpi-users" />
        </div>
      )}

      {/* Action bar */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div className="flex flex-wrap items-center gap-3">
          <input
            type="text"
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            placeholder="Search by email, order ID, or address…"
            className="flex-1 min-w-[220px] bg-gray-900 border border-gray-700 text-white px-3 py-2 rounded-lg text-sm"
            data-testid="payments-search"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-white px-3 py-2 rounded-lg text-sm"
            data-testid="payments-status-filter"
          >
            <option value="all">All statuses</option>
            <option value="paid">✅ Paid</option>
            <option value="pending">⏳ Pending</option>
            <option value="finished">finished</option>
            <option value="confirmed">confirmed</option>
            <option value="waiting">waiting</option>
            <option value="failed">failed</option>
            <option value="expired">expired</option>
          </select>
          <button onClick={fetchOrders} className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium" data-testid="payments-refresh">
            🔄 Refresh
          </button>
          <button onClick={downloadCsv} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium" data-testid="payments-export-csv">
            📥 Export CSV
          </button>
          <button onClick={() => setShowGrant(true)} className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium" data-testid="payments-grant-btn">
            ⭐ Grant Access
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Orders table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
          <h3 className="text-white font-semibold">Orders</h3>
          <span className="text-xs text-gray-400" data-testid="orders-total">{total} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-900/50 text-gray-400 uppercase text-xs">
              <tr>
                <th className="px-4 py-3 text-left">Order ID</th>
                <th className="px-4 py-3 text-left">Email</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-left">Currency</th>
                <th className="px-4 py-3 text-left">Created</th>
                <th className="px-4 py-3 text-left">Confirmed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {loading && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-500">Loading…</td></tr>
              )}
              {!loading && orders.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-500">No orders found</td></tr>
              )}
              {!loading && orders.map((o) => (
                <tr key={o.order_id} className="hover:bg-gray-700/30" data-testid={`order-row-${o.order_id}`}>
                  <td className="px-4 py-2 text-gray-300 font-mono text-xs">{o.order_id}</td>
                  <td className="px-4 py-2 text-gray-200">{o.user_email || '—'}</td>
                  <td className="px-4 py-2"><StatusBadge status={o.status} /></td>
                  <td className="px-4 py-2 text-right text-gray-200">${(o.price || 0).toFixed(2)}</td>
                  <td className="px-4 py-2 text-gray-400 uppercase text-xs">{o.pay_currency || '—'}</td>
                  <td className="px-4 py-2 text-gray-400 text-xs">{fmtDate(o.created_at)}</td>
                  <td className="px-4 py-2 text-gray-400 text-xs">{fmtDate(o.confirmed_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Grant Access Modal */}
      {showGrant && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50" onClick={() => setShowGrant(false)}>
          <div className="bg-gray-800 rounded-xl border border-gray-700 max-w-md w-full p-6" onClick={(e) => e.stopPropagation()} data-testid="grant-access-modal">
            <h3 className="text-xl font-bold text-white mb-1">Grant Lifetime Access</h3>
            <p className="text-sm text-gray-400 mb-4">Manually grant Premium access to an existing user (e.g. gift, comp, support refund).</p>
            <form onSubmit={submitGrant} className="space-y-3">
              <div>
                <label className="block text-xs text-gray-400 uppercase tracking-wider mb-1">User Email</label>
                <input
                  type="email"
                  value={grantEmail}
                  onChange={(e) => setGrantEmail(e.target.value)}
                  required
                  placeholder="user@example.com"
                  className="w-full bg-gray-900 border border-gray-700 text-white px-3 py-2 rounded-lg"
                  data-testid="grant-email-input"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-400 uppercase tracking-wider mb-1">Note (optional)</label>
                <input
                  type="text"
                  value={grantNote}
                  onChange={(e) => setGrantNote(e.target.value)}
                  placeholder="e.g. Gift from owner / paid via PIX out-of-band"
                  className="w-full bg-gray-900 border border-gray-700 text-white px-3 py-2 rounded-lg"
                  data-testid="grant-note-input"
                />
              </div>
              {grantResult && (
                <div className={`text-sm px-3 py-2 rounded-lg ${grantResult.ok ? 'bg-green-900/40 text-green-300 border border-green-800' : 'bg-red-900/40 text-red-300 border border-red-800'}`} data-testid="grant-result">
                  {grantResult.message}
                </div>
              )}
              <div className="flex gap-2 justify-end pt-2">
                <button type="button" onClick={() => setShowGrant(false)} className="text-gray-400 hover:text-white px-4 py-2 rounded-lg text-sm">Cancel</button>
                <button type="submit" disabled={granting} className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50" data-testid="grant-submit-btn">
                  {granting ? 'Granting…' : 'Grant Access'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

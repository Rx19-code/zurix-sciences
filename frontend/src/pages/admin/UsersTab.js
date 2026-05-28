import React, { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function KpiCard({ label, value, accent, testid }) {
  return (
    <div className={`bg-gray-800 rounded-xl p-4 border-l-4 ${accent}`} data-testid={testid}>
      <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}

function ProviderBadge({ provider }) {
  const isGoogle = provider === 'google';
  const cls = isGoogle
    ? 'bg-blue-600 text-white'
    : 'bg-purple-600 text-white';
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold uppercase ${cls}`}
      data-testid={`provider-badge-${provider}`}
    >
      {provider || 'unknown'}
    </span>
  );
}

function LifetimeBadge({ hasLifetime }) {
  return hasLifetime ? (
    <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold uppercase bg-yellow-500 text-gray-900" data-testid="lifetime-yes">
      Lifetime
    </span>
  ) : (
    <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold uppercase bg-gray-600 text-gray-200" data-testid="lifetime-no">
      Free
    </span>
  );
}

export default function UsersTab({ adminPassword }) {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({ total_all: 0, total_lifetime: 0, total_google: 0, total_email: 0 });
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [search, setSearch] = useState('');
  const [provider, setProvider] = useState('');
  const [lifetime, setLifetime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const PAGE_SIZE = 50;

  const fetchUsers = useCallback(async (resetSkip = false) => {
    setLoading(true);
    setError('');
    const currentSkip = resetSkip ? 0 : skip;
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (provider) params.append('provider', provider);
      if (lifetime) params.append('lifetime', lifetime);
      params.append('limit', PAGE_SIZE);
      params.append('skip', currentSkip);

      const res = await fetch(`${API_URL}/api/admin/users?${params.toString()}`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setUsers(data.users || []);
      setStats(data.stats || {});
      setTotal(data.total || 0);
      setHasMore(data.has_more || false);
      if (resetSkip) setSkip(0);
    } catch (e) {
      setError(e.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [adminPassword, search, provider, lifetime, skip]);

  useEffect(() => {
    fetchUsers(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchUsers(true);
  };

  const handleNextPage = () => {
    const newSkip = skip + PAGE_SIZE;
    setSkip(newSkip);
    setTimeout(() => fetchUsers(false), 0);
  };

  const handlePrevPage = () => {
    const newSkip = Math.max(0, skip - PAGE_SIZE);
    setSkip(newSkip);
    setTimeout(() => fetchUsers(false), 0);
  };

  const handleExportCsv = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/users/export`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'zurix_users.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (userId, email) => {
    if (!window.confirm(`Permanently delete user ${email}? This cannot be undone.`)) return;
    try {
      const res = await fetch(`${API_URL}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error('Delete failed');
      fetchUsers(false);
    } catch (e) {
      setError(e.message);
    }
  };

  const fmtDate = (iso) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    } catch {
      return iso.slice(0, 16);
    }
  };

  return (
    <div className="space-y-6" data-testid="users-tab">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="Total Users" value={stats.total_all || 0} accent="border-blue-500" testid="kpi-total-users" />
        <KpiCard label="Lifetime Access" value={stats.total_lifetime || 0} accent="border-yellow-500" testid="kpi-lifetime-users" />
        <KpiCard label="Email Auth" value={stats.total_email || 0} accent="border-purple-500" testid="kpi-email-users" />
        <KpiCard label="Google Auth" value={stats.total_google || 0} accent="border-green-500" testid="kpi-google-users" />
      </div>

      {/* Filters + Export */}
      <div className="bg-gray-800 rounded-2xl p-5 border border-gray-700">
        <form onSubmit={handleSearch} className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs text-gray-400 uppercase mb-1">Search email / name</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="john@example.com"
              data-testid="users-search-input"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 uppercase mb-1">Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              data-testid="users-filter-provider"
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="">All</option>
              <option value="email">Email</option>
              <option value="google">Google</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 uppercase mb-1">Lifetime</label>
            <select
              value={lifetime}
              onChange={(e) => setLifetime(e.target.value)}
              data-testid="users-filter-lifetime"
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="">All</option>
              <option value="yes">With Lifetime</option>
              <option value="no">Without</option>
            </select>
          </div>
          <button
            type="submit"
            data-testid="users-search-btn"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
          >
            🔍 Search
          </button>
          <button
            type="button"
            onClick={handleExportCsv}
            data-testid="users-export-csv-btn"
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition"
          >
            ⬇ Export CSV
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/40 border border-red-700 text-red-200 px-4 py-3 rounded-lg" data-testid="users-error">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-700 flex justify-between items-center">
          <h3 className="text-lg font-bold text-white">
            Registered Users{' '}
            <span className="text-sm text-gray-400 font-normal">
              ({total} total{search || provider || lifetime ? ' • filtered' : ''})
            </span>
          </h3>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-400" data-testid="users-loading">Loading...</div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center text-gray-400" data-testid="users-empty">No users found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="users-table">
              <thead className="bg-gray-900/60 text-gray-400 uppercase text-xs">
                <tr>
                  <th className="px-4 py-3 text-left">Email</th>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Provider</th>
                  <th className="px-4 py-3 text-left">Access</th>
                  <th className="px-4 py-3 text-left">Joined</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {users.map((u) => (
                  <tr key={u.id} className="text-gray-200 hover:bg-gray-700/40 transition" data-testid={`user-row-${u.id}`}>
                    <td className="px-4 py-3 font-mono text-xs">{u.email}</td>
                    <td className="px-4 py-3">{u.name || '—'}</td>
                    <td className="px-4 py-3"><ProviderBadge provider={u.auth_provider} /></td>
                    <td className="px-4 py-3"><LifetimeBadge hasLifetime={u.has_lifetime_access} /></td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{fmtDate(u.created_at)}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleDelete(u.id, u.email)}
                        data-testid={`delete-user-${u.id}`}
                        className="px-3 py-1 bg-red-700 hover:bg-red-600 text-white text-xs font-semibold rounded transition"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {!loading && users.length > 0 && (
          <div className="px-5 py-3 border-t border-gray-700 flex justify-between items-center">
            <p className="text-xs text-gray-400">
              Showing {skip + 1}–{skip + users.length} of {total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={handlePrevPage}
                disabled={skip === 0}
                data-testid="users-prev-page"
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-semibold rounded transition"
              >
                ← Prev
              </button>
              <button
                onClick={handleNextPage}
                disabled={!hasMore}
                data-testid="users-next-page"
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-semibold rounded transition"
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

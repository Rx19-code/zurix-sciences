import React, { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function KpiCard({ label, value, accent, testid }) {
  return (
    <div className={`bg-gray-800 rounded-xl p-4 border-l-4 ${accent}`} data-testid={testid}>
      <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value.toLocaleString()}</p>
    </div>
  );
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function daysAgoISO(days) {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

function monthStartISO() {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10);
}

export default function VerificationsTab({ adminPassword }) {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [topBatches, setTopBatches] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [batchFilter, setBatchFilter] = useState('');
  const [codeFilter, setCodeFilter] = useState('');

  const PAGE_SIZE = 50;

  const fetchData = useCallback(async (resetSkip = false) => {
    setLoading(true);
    setError('');
    const currentSkip = resetSkip ? 0 : skip;
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (batchFilter) params.append('batch_number', batchFilter);
      if (codeFilter) params.append('code', codeFilter);
      params.append('limit', PAGE_SIZE);
      params.append('skip', currentSkip);

      const res = await fetch(`${API_URL}/api/admin/verifications?${params.toString()}`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setLogs(data.logs || []);
      setStats(data.stats || {});
      setTopBatches(data.top_batches || []);
      setTotal(data.total || 0);
      setHasMore(data.has_more || false);
      if (resetSkip) setSkip(0);
    } catch (e) {
      setError(e.message || 'Failed to load verifications');
    } finally {
      setLoading(false);
    }
  }, [adminPassword, startDate, endDate, batchFilter, codeFilter, skip]);

  useEffect(() => {
    fetchData(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchData(true);
  };

  const handleQuickRange = (range) => {
    if (range === 'today') {
      setStartDate(todayISO());
      setEndDate(todayISO());
    } else if (range === '7d') {
      setStartDate(daysAgoISO(7));
      setEndDate(todayISO());
    } else if (range === '30d') {
      setStartDate(daysAgoISO(30));
      setEndDate(todayISO());
    } else if (range === 'month') {
      setStartDate(monthStartISO());
      setEndDate(todayISO());
    } else if (range === 'clear') {
      setStartDate('');
      setEndDate('');
    }
    setTimeout(() => fetchData(true), 0);
  };

  const handleExportCsv = async () => {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (batchFilter) params.append('batch_number', batchFilter);

      const res = await fetch(`${API_URL}/api/admin/verifications/export?${params.toString()}`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const range = startDate && endDate ? `_${startDate}_to_${endDate}` : '';
      a.download = `zurix_verifications${range}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleNextPage = () => {
    const newSkip = skip + PAGE_SIZE;
    setSkip(newSkip);
    setTimeout(() => fetchData(false), 0);
  };

  const handlePrevPage = () => {
    const newSkip = Math.max(0, skip - PAGE_SIZE);
    setSkip(newSkip);
    setTimeout(() => fetchData(false), 0);
  };

  const fmtTs = (iso) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('en-US', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit',
      });
    } catch {
      return iso.slice(0, 16);
    }
  };

  return (
    <div className="space-y-6" data-testid="verifications-tab">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard label="Today" value={stats.total_today || 0} accent="border-yellow-500" testid="kpi-verif-today" />
        <KpiCard label="Last 7 days" value={stats.total_7d || 0} accent="border-orange-500" testid="kpi-verif-7d" />
        <KpiCard label="This Month" value={stats.total_month || 0} accent="border-green-500" testid="kpi-verif-month" />
        <KpiCard label="Last 30 days" value={stats.total_30d || 0} accent="border-blue-500" testid="kpi-verif-30d" />
        <KpiCard label="This Year" value={stats.total_year || 0} accent="border-purple-500" testid="kpi-verif-year" />
        <KpiCard label="All Time" value={stats.total_all || 0} accent="border-pink-500" testid="kpi-verif-all" />
      </div>

      {/* Top Batches */}
      {topBatches.length > 0 && (
        <div className="bg-gray-800 rounded-2xl p-5 border border-gray-700">
          <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-3">Top 5 Most Verified Batches</h3>
          <div className="flex flex-wrap gap-2">
            {topBatches.map((b) => (
              <button
                key={b.batch}
                onClick={() => { setBatchFilter(b.batch); setTimeout(() => fetchData(true), 0); }}
                className="px-3 py-1.5 bg-gray-700 hover:bg-blue-700 text-white text-xs font-mono rounded-lg transition"
                data-testid={`top-batch-${b.batch}`}
              >
                {b.batch} <span className="ml-2 text-yellow-400">×{b.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Filters + Quick ranges + Export */}
      <div className="bg-gray-800 rounded-2xl p-5 border border-gray-700 space-y-4">
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-400 uppercase self-center mr-2">Quick:</span>
          {['today', '7d', '30d', 'month'].map(r => (
            <button
              key={r}
              onClick={() => handleQuickRange(r)}
              data-testid={`quick-range-${r}`}
              className="px-3 py-1 bg-gray-700 hover:bg-blue-600 text-white text-xs font-semibold rounded transition"
            >
              {r === 'today' ? 'Today' : r === '7d' ? 'Last 7d' : r === '30d' ? 'Last 30d' : 'This Month'}
            </button>
          ))}
          <button
            onClick={() => handleQuickRange('clear')}
            data-testid="quick-range-clear"
            className="px-3 py-1 bg-red-700 hover:bg-red-600 text-white text-xs font-semibold rounded transition"
          >
            Clear
          </button>
        </div>

        <form onSubmit={handleSearch} className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-xs text-gray-400 uppercase mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              data-testid="verif-start-date"
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 uppercase mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              data-testid="verif-end-date"
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex-1 min-w-[180px]">
            <label className="block text-xs text-gray-400 uppercase mb-1">Batch Number</label>
            <input
              type="text"
              value={batchFilter}
              onChange={(e) => setBatchFilter(e.target.value)}
              placeholder="ZX-260115-BPC157-1"
              data-testid="verif-batch-filter"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono text-sm"
            />
          </div>
          <div className="flex-1 min-w-[180px]">
            <label className="block text-xs text-gray-400 uppercase mb-1">Code</label>
            <input
              type="text"
              value={codeFilter}
              onChange={(e) => setCodeFilter(e.target.value)}
              placeholder="Partial code..."
              data-testid="verif-code-filter"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono text-sm"
            />
          </div>
          <button
            type="submit"
            data-testid="verif-search-btn"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
          >
            🔍 Search
          </button>
          <button
            type="button"
            onClick={handleExportCsv}
            data-testid="verif-export-csv-btn"
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition"
          >
            ⬇ Export CSV
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/40 border border-red-700 text-red-200 px-4 py-3 rounded-lg" data-testid="verif-error">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-700">
          <h3 className="text-lg font-bold text-white">
            Verification Logs{' '}
            <span className="text-sm text-gray-400 font-normal">
              ({total.toLocaleString()} total{startDate || endDate || batchFilter || codeFilter ? ' • filtered' : ''})
            </span>
          </h3>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-400" data-testid="verif-loading">Loading...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-gray-400" data-testid="verif-empty">No verifications found in this range.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="verif-table">
              <thead className="bg-gray-900/60 text-gray-400 uppercase text-xs">
                <tr>
                  <th className="px-4 py-3 text-left">Timestamp</th>
                  <th className="px-4 py-3 text-left">Code</th>
                  <th className="px-4 py-3 text-left">Batch</th>
                  <th className="px-4 py-3 text-left">Product</th>
                  <th className="px-4 py-3 text-center">Verif. #</th>
                  <th className="px-4 py-3 text-left">Location</th>
                  <th className="px-4 py-3 text-left">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {logs.map((log) => (
                  <tr key={log.id} className="text-gray-200 hover:bg-gray-700/40 transition" data-testid={`verif-row-${log.id}`}>
                    <td className="px-4 py-3 text-xs text-gray-400">{fmtTs(log.timestamp)}</td>
                    <td className="px-4 py-3 font-mono text-xs">{log.code || log.verification_code || '—'}</td>
                    <td className="px-4 py-3 font-mono text-xs">{log.batch_number || '—'}</td>
                    <td className="px-4 py-3">{log.product_name || '—'}</td>
                    <td className="px-4 py-3 text-center">
                      {log.verification_number ? (
                        <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold ${
                          log.verification_number > 5 ? 'bg-red-600 text-white' : log.verification_number > 1 ? 'bg-yellow-500 text-gray-900' : 'bg-green-600 text-white'
                        }`}>
                          {log.verification_number}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="px-4 py-3 text-xs">
                      {log.country ? `${log.country_code || ''} ${log.city || ''}, ${log.country}` : '—'}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-400">{log.client_ip || log.ip || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {!loading && logs.length > 0 && (
          <div className="px-5 py-3 border-t border-gray-700 flex justify-between items-center">
            <p className="text-xs text-gray-400">
              Showing {skip + 1}–{skip + logs.length} of {total.toLocaleString()}
            </p>
            <div className="flex gap-2">
              <button
                onClick={handlePrevPage}
                disabled={skip === 0}
                data-testid="verif-prev-page"
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-semibold rounded transition"
              >
                ← Prev
              </button>
              <button
                onClick={handleNextPage}
                disabled={!hasMore}
                data-testid="verif-next-page"
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

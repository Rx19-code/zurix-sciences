import React, { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const AUTO_REFRESH_MS = 30_000;

const SEV_STYLES = {
  green:  { dot: 'bg-green-500',  ring: 'ring-green-500/40',  text: 'text-green-400',  bg: 'bg-green-950/30 border-green-900/50' },
  yellow: { dot: 'bg-amber-400',  ring: 'ring-amber-400/40',  text: 'text-amber-300',  bg: 'bg-amber-950/30 border-amber-900/50' },
  red:    { dot: 'bg-red-500',    ring: 'ring-red-500/40',    text: 'text-red-400',    bg: 'bg-red-950/30 border-red-900/50' },
};

export default function HealthTab({ adminPassword }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastFetched, setLastFetched] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchHealth = useCallback(async () => {
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/admin/health`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setLastFetched(new Date());
    } catch (e) {
      console.error('HealthTab: failed to fetch health', e);
      setError(e.message || 'Failed to load health data');
    } finally {
      setLoading(false);
    }
  }, [adminPassword]);

  useEffect(() => {
    fetchHealth();
    if (!autoRefresh) return undefined;
    const t = setInterval(fetchHealth, AUTO_REFRESH_MS);
    return () => clearInterval(t);
  }, [fetchHealth, autoRefresh]);

  if (loading && !data) {
    return <p className="text-gray-400" data-testid="health-loading">Loading system health...</p>;
  }

  const checks = data?.checks || {};
  const overall = data?.overall_severity || 'green';
  const ov = SEV_STYLES[overall];

  return (
    <div className="space-y-6" data-testid="health-tab">
      {/* Overall banner */}
      <div className={`rounded-2xl border p-5 flex items-center justify-between flex-wrap gap-3 ${ov.bg}`}>
        <div className="flex items-center gap-4">
          <span className={`w-4 h-4 rounded-full ring-4 ${ov.ring} ${ov.dot}`} />
          <div>
            <h2 className={`text-lg font-bold ${ov.text} uppercase tracking-wide`}>
              System Status: {overall}
            </h2>
            <p className="text-xs text-gray-400">
              {overall === 'green' && 'All systems operational.'}
              {overall === 'yellow' && 'Attention needed — one or more subsystems have warnings.'}
              {overall === 'red' && 'Critical issue detected — action required.'}
              {lastFetched && ` • Last refresh: ${lastFetched.toLocaleTimeString()}`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
            <input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)}
              data-testid="health-auto-refresh" className="w-4 h-4 accent-blue-600" />
            Auto-refresh 30s
          </label>
          <button type="button" onClick={fetchHealth}
            data-testid="health-refresh-btn"
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition">
            Refresh now
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/40 border border-red-700 text-red-200 px-4 py-2 rounded-lg text-sm" data-testid="health-error">
          {error}
        </div>
      )}

      {/* Cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <MongoCard check={checks.mongo} />
        <BackupCard check={checks.backup} />
        <DiskCard check={checks.disk} />
        <MemoryCard check={checks.memory} />
        <UptimeCard check={checks.uptime} />
        <ErrorsCard check={checks.errors} />
      </div>
    </div>
  );
}

/* ─── Card primitives ────────────────────────────────────────────────────── */
function Card({ title, icon, check, children }) {
  const sev = check?.severity || 'green';
  const s = SEV_STYLES[sev];
  return (
    <div className={`rounded-2xl border p-5 ${s.bg}`} data-testid={`health-card-${title.toLowerCase().replace(/\s+/g,'-')}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <h3 className="font-bold text-white">{title}</h3>
        </div>
        <span className={`w-3 h-3 rounded-full ${s.dot}`} />
      </div>
      {check?.error && (
        <div className="text-xs text-amber-300 bg-amber-950/40 border border-amber-900/50 rounded px-2 py-1 mb-2">
          {check.error}
        </div>
      )}
      {children}
    </div>
  );
}

function Row({ label, value, mono }) {
  return (
    <div className="flex items-center justify-between text-sm py-1">
      <span className="text-gray-400 text-xs uppercase tracking-wider">{label}</span>
      <span className={`text-gray-100 ${mono ? 'font-mono text-xs' : ''}`}>{value ?? '—'}</span>
    </div>
  );
}

function Bar({ percent, sev }) {
  const p = Math.max(0, Math.min(100, percent || 0));
  const color = sev === 'red' ? 'bg-red-500' : sev === 'yellow' ? 'bg-amber-400' : 'bg-green-500';
  return (
    <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
      <div className={`h-full ${color} transition-all`} style={{ width: `${p}%` }} />
    </div>
  );
}

/* ─── Individual cards ───────────────────────────────────────────────────── */
function MongoCard({ check }) {
  if (!check) return <Card title="MongoDB" icon="🗄️" check={check} />;
  const counts = check.counts || {};
  const topCollections = Object.entries(counts)
    .filter(([, v]) => v > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  return (
    <Card title="MongoDB" icon="🗄️" check={check}>
      <Row label="Version" value={check.version} mono />
      <Row label="Database" value={check.db_name} mono />
      <Row label="Data size" value={check.data_size} />
      <Row label="Storage" value={check.storage_size} />
      <Row label="Objects" value={check.objects?.toLocaleString()} />
      <Row label="Collections" value={check.collections_count} />
      {topCollections.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700/50">
          <div className="text-[10px] uppercase text-gray-500 mb-1 tracking-wider">Top collections</div>
          {topCollections.map(([name, count]) => (
            <div key={name} className="flex justify-between text-xs py-0.5">
              <span className="text-gray-400">{name}</span>
              <span className="font-mono text-gray-200">{count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

function BackupCard({ check }) {
  return (
    <Card title="Backup" icon="💾" check={check}>
      <Row label="Latest" value={check?.latest_file} mono />
      <Row label="Age" value={check?.latest_age_hours != null ? `${check.latest_age_hours}h ago` : '—'} />
      <Row label="Size" value={check?.latest_size} />
      <Row label="Total backups" value={check?.total_backups} />
      <Row label="Total size" value={check?.total_size} />
      <Row label="Location" value={check?.backups_dir} mono />
    </Card>
  );
}

function DiskCard({ check }) {
  return (
    <Card title="Disk" icon="💽" check={check}>
      <div className="mb-3">
        <div className="flex justify-between mb-1 text-sm">
          <span className="text-gray-300">{check?.used} used</span>
          <span className={`font-bold ${SEV_STYLES[check?.severity || 'green'].text}`}>{check?.percent_used}%</span>
        </div>
        <Bar percent={check?.percent_used} sev={check?.severity} />
      </div>
      <Row label="Total" value={check?.total} />
      <Row label="Free" value={check?.free} />
    </Card>
  );
}

function MemoryCard({ check }) {
  return (
    <Card title="Memory" icon="🧠" check={check}>
      <div className="mb-3">
        <div className="flex justify-between mb-1 text-sm">
          <span className="text-gray-300">{check?.used} used</span>
          <span className={`font-bold ${SEV_STYLES[check?.severity || 'green'].text}`}>{check?.percent_used}%</span>
        </div>
        <Bar percent={check?.percent_used} sev={check?.severity} />
      </div>
      <Row label="Total" value={check?.total} />
      <Row label="Available" value={check?.available} />
    </Card>
  );
}

function UptimeCard({ check }) {
  return (
    <Card title="Uptime" icon="⏱️" check={check}>
      <Row label="System" value={check?.system_uptime} />
      <Row label="Backend" value={check?.backend_uptime} />
      <Row label="Python" value={check?.python_version} mono />
      <Row label="Platform" value={check?.platform ? check.platform.split('-')[0] : '—'} mono />
    </Card>
  );
}

function ErrorsCard({ check }) {
  const lines = check?.lines || [];
  const errorLines = lines.filter((l) => /error|exception|traceback|fail/i.test(l));
  return (
    <Card title="Recent errors" icon="⚠️" check={check}>
      <Row label="Log file" value={check?.log_file ? check.log_file.split('/').pop() : '—'} mono />
      <Row label="Errors seen" value={errorLines.length} />
      {errorLines.length > 0 ? (
        <div className="mt-2 max-h-32 overflow-y-auto bg-gray-950/60 rounded p-2 border border-gray-700/50">
          {errorLines.slice(-5).map((line, i) => (
            <div key={`${i}-${line.slice(0,20)}`} className="text-[10px] font-mono text-red-300 py-0.5 break-all">
              {line.length > 200 ? `${line.slice(0, 200)}…` : line}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-gray-500 mt-2">No recent errors in log.</p>
      )}
    </Card>
  );
}

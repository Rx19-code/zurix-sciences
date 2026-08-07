import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Country centroid fallback for scans logged before lat/lon collection
const CENTROIDS = {
  US: [39.8, -98.6], BR: [-14.2, -51.9], PY: [-23.4, -58.4], AR: [-38.4, -63.6],
  UY: [-32.5, -55.8], CL: [-35.7, -71.5], PE: [-9.2, -75.0], CO: [4.6, -74.3],
  MX: [23.6, -102.5], CA: [56.1, -106.3], EC: [-1.8, -78.2], BO: [-16.3, -63.6],
  VE: [6.4, -66.6], PA: [8.5, -80.8], CR: [9.7, -83.8], GT: [15.8, -90.2], DO: [18.7, -70.2],
  CH: [46.8, 8.2], DE: [51.2, 10.4], FR: [46.6, 2.2], ES: [40.5, -3.7], PT: [39.4, -8.2],
  IT: [41.9, 12.6], GB: [55.4, -3.4], IE: [53.4, -8.2], NL: [52.1, 5.3], BE: [50.5, 4.5],
  AT: [47.5, 14.6], PL: [51.9, 19.1], CZ: [49.8, 15.5], SE: [60.1, 18.6], NO: [60.5, 8.5],
  DK: [56.3, 9.5], FI: [61.9, 25.7], GR: [39.1, 21.8], RO: [45.9, 24.9], HU: [47.2, 19.5],
  RU: [61.5, 105.3], UA: [48.4, 31.2], TR: [39.0, 35.2], IL: [31.0, 34.9], AE: [23.4, 53.8],
  SA: [23.9, 45.1], ZA: [-30.6, 22.9], EG: [26.8, 30.8], NG: [9.1, 8.7], MA: [31.8, -7.1],
  AU: [-25.3, 133.8], NZ: [-40.9, 174.9], JP: [36.2, 138.3], KR: [35.9, 127.8],
  CN: [35.9, 104.2], IN: [20.6, 79.0], TH: [15.9, 100.9], VN: [14.1, 108.3],
  PH: [12.9, 121.8], ID: [-0.8, 113.9], MY: [4.2, 102.0], SG: [1.35, 103.8],
};

export default function ScanMapTab({ password, apiUrl }) {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');
  const mapRef = useRef(null);
  const mapInstance = useRef(null);

  useEffect(() => {
    fetch(`${apiUrl}/api/admin/verifications/geo-stats`, { headers: { 'x-admin-password': password } })
      .then(r => r.json())
      .then(setStats)
      .catch(() => setError('Failed to load geo stats'));
  }, [apiUrl, password]);

  useEffect(() => {
    if (!stats || !mapRef.current || mapInstance.current) return;
    const map = L.map(mapRef.current, { worldCopyJump: true }).setView([15, -30], 2);
    mapInstance.current = map;
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      maxZoom: 12,
    }).addTo(map);

    const maxCount = Math.max(1, ...stats.cities.map(c => c.count));
    stats.cities.forEach(c => {
      let pos = (c.lat != null && c.lon != null) ? [c.lat, c.lon] : CENTROIDS[c.country_code];
      if (!pos) return;
      const radius = 6 + (c.count / maxCount) * 18;
      L.circleMarker(pos, {
        radius,
        color: '#22c55e',
        fillColor: '#22c55e',
        fillOpacity: 0.45,
        weight: 1.5,
      })
        .bindPopup(`<b>${c.city}, ${c.country}</b><br/>${c.count} scan${c.count > 1 ? 's' : ''}<br/><small>Last: ${(c.last_scan || '').slice(0, 16).replace('T', ' ')}</small>`)
        .addTo(map);
    });

    return () => { map.remove(); mapInstance.current = null; };
  }, [stats]);

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700" data-testid="scan-map-tab">
      <h2 className="text-xl font-bold text-white mb-2">Verification Scan Map</h2>
      <p className="text-gray-400 text-sm mb-6">Where customers scan QR codes worldwide (based on verification logs geolocation)</p>

      {error && <div className="p-4 rounded-lg bg-red-900/50 border border-red-500 text-red-400 mb-4">{error}</div>}

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard label="Total Scans" value={stats.total_scans} testid="scanmap-total" />
          <StatCard label="Located Scans" value={stats.located_scans} testid="scanmap-located" />
          <StatCard label="Countries" value={stats.countries.length} testid="scanmap-countries" />
          <StatCard label="Cities" value={stats.cities.length} testid="scanmap-cities" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div ref={mapRef} className="w-full rounded-xl overflow-hidden border border-gray-700" style={{ height: '480px' }} data-testid="scan-map-container" />
        </div>

        <div className="bg-gray-900/60 rounded-xl border border-gray-700 p-4 max-h-[480px] overflow-y-auto">
          <h3 className="text-white font-semibold mb-3 text-sm uppercase tracking-wide">Top Countries</h3>
          {stats?.countries?.length === 0 && <p className="text-gray-500 text-sm">No located scans yet.</p>}
          <div className="space-y-2">
            {stats?.countries?.map(c => (
              <div key={c.country_code} className="flex items-center gap-3 bg-gray-800/70 rounded-lg px-3 py-2" data-testid={`scanmap-country-${c.country_code}`}>
                <img src={`https://flagcdn.com/w40/${(c.country_code || 'un').toLowerCase()}.png`} alt={c.country} className="w-8 h-6 rounded object-cover" onError={(e) => { e.target.style.display = 'none'; }} />
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium truncate">{c.country}</p>
                  <p className="text-gray-500 text-xs">Last: {(c.last_scan || '').slice(0, 10)}</p>
                </div>
                <span className="text-emerald-400 font-bold text-lg">{c.count}</span>
              </div>
            ))}
          </div>

          {stats?.cities?.length > 0 && (
            <>
              <h3 className="text-white font-semibold mt-5 mb-3 text-sm uppercase tracking-wide">Top Cities</h3>
              <div className="space-y-1">
                {stats.cities.slice(0, 15).map((c, i) => (
                  <div key={i} className="flex justify-between text-sm px-3 py-1.5 rounded bg-gray-800/40">
                    <span className="text-gray-300 truncate">{c.city}, {c.country_code}</span>
                    <span className="text-emerald-400 font-semibold ml-2">{c.count}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

const StatCard = ({ label, value, testid }) => (
  <div className="bg-gray-900/60 rounded-xl border border-gray-700 p-4" data-testid={testid}>
    <p className="text-gray-500 text-xs uppercase tracking-wide">{label}</p>
    <p className="text-white text-2xl font-bold mt-1">{value}</p>
  </div>
);

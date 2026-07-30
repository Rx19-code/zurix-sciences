import React, { useState, useEffect } from 'react';

export default function BrandQRTab({ password, apiUrl }) {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [downloading, setDownloading] = useState(null);
  const [transparent, setTransparent] = useState(false);

  useEffect(() => {
    let objectUrl = null;
    fetch(`${apiUrl}/api/admin/brand-qr?size=600`, { headers: { 'x-admin-password': password } })
      .then(r => r.blob())
      .then(blob => {
        objectUrl = URL.createObjectURL(blob);
        setPreviewUrl(objectUrl);
      })
      .catch(() => {});
    return () => { if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [apiUrl, password]);

  const download = async (size, label) => {
    setDownloading(size);
    try {
      const res = await fetch(`${apiUrl}/api/admin/brand-qr?size=${size}${transparent ? '&transparent=true' : ''}`, { headers: { 'x-admin-password': password } });
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `zurix-brand-qr-${label}${transparent ? '-transparent' : ''}.png`;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch {}
    setDownloading(null);
  };

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700" data-testid="brand-qr-tab">
      <h2 className="text-xl font-bold text-white mb-2">Brand QR Code</h2>
      <p className="text-gray-400 text-sm mb-6">
        Fixed QR pointing to <span className="text-blue-400 font-mono">https://zurixsciences.com</span> — it is deterministic:
        the exact same QR is generated every time, forever. Safe to print on product boxes, keychains and merchandise.
      </p>

      <div className="flex flex-col md:flex-row gap-8 items-start">
        <div className="bg-white rounded-xl p-4" data-testid="brand-qr-preview">
          {previewUrl ? (
            <img src={previewUrl} alt="Zurix Brand QR" className="w-64 h-64" />
          ) : (
            <div className="w-64 h-64 flex items-center justify-center text-gray-400">Loading...</div>
          )}
        </div>

        <div className="space-y-3 flex-1">
          <h3 className="text-white font-semibold">Download for print</h3>
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer select-none" data-testid="brand-qr-transparent-toggle">
            <input
              type="checkbox"
              checked={transparent}
              onChange={(e) => setTransparent(e.target.checked)}
              className="w-4 h-4 accent-blue-600"
            />
            Transparent background (PNG with alpha — for colored boxes/artwork)
          </label>
          {[
            { size: 1000, label: '1000px', desc: 'Small prints — stickers, keychains (~3cm)' },
            { size: 2000, label: '2000px', desc: 'Product boxes, packaging (~8cm)' },
            { size: 4000, label: '4000px', desc: 'Large format — banners, posters' },
          ].map(o => (
            <button
              key={o.size}
              onClick={() => download(o.size, o.label)}
              disabled={downloading === o.size}
              className="w-full md:w-auto flex items-center gap-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold px-5 py-3 rounded-lg transition"
              data-testid={`brand-qr-download-${o.size}`}
            >
              ⬇️ PNG {o.label}
              <span className="text-blue-200 text-xs font-normal">{o.desc}</span>
            </button>
          ))}
          <p className="text-gray-500 text-xs mt-4">
            300 DPI, high error correction (30%) — scans reliably even with the ZX center badge or minor print damage.
          </p>
        </div>
      </div>
    </div>
  );
}

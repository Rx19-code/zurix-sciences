import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';

const todayStr = () => new Date().toISOString().slice(0, 10);
const EXPIRY_OPTIONS = [3, 6, 12, 18, 24, 36];

export default function GenerateCodesPanel({ password, apiUrl, products, onGenerated }) {
  const [productId, setProductId] = useState('');
  const [productName, setProductName] = useState('');
  const [productCode, setProductCode] = useState('');
  const [sequence, setSequence] = useState(1);
  const [fabDate, setFabDate] = useState(todayStr());
  const [quantity, setQuantity] = useState(50);
  const [purity, setPurity] = useState('≥99%');
  const [expiryMonths, setExpiryMonths] = useState(24);
  const [suggestion, setSuggestion] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!productId) return;
    fetch(`${apiUrl}/api/admin/batch-suggestion?product_id=${encodeURIComponent(productId)}`, {
      headers: { 'x-admin-password': password }
    })
      .then(r => r.json())
      .then(data => {
        setSuggestion(data);
        if (data.found) {
          setProductCode(data.product_code);
          setSequence(data.next_sequence);
        } else {
          setProductCode('');
          setSequence(1);
        }
      })
      .catch(() => setSuggestion(null));
  }, [productId, apiUrl, password]);

  const cleanCode = productCode.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  const yymmdd = fabDate ? fabDate.slice(2).replace(/-/g, '') : '';
  const batchPreview = cleanCode && fabDate ? `ZX-${yymmdd}-${cleanCode}-${sequence}` : '';
  const codePreview = cleanCode ? `ZX${cleanCode}${sequence}xxxxxx` : '';
  const expiryPreview = (() => {
    if (!fabDate) return '';
    const y = parseInt(fabDate.slice(0, 4));
    const m = parseInt(fabDate.slice(5, 7)) - 1;
    const total = m + (parseInt(expiryMonths) || 24);
    return `${y + Math.floor(total / 12)}-${String((total % 12) + 1).padStart(2, '0')}-01`;
  })();

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!productId || !cleanCode || !fabDate || !quantity) {
      setError('Please fill all fields');
      return;
    }
    setGenerating(true);
    try {
      const res = await fetch(`${apiUrl}/api/admin/generate-codes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-admin-password': password },
        body: JSON.stringify({
          product_id: productId,
          product_name: productName,
          product_code: cleanCode,
          sequence: parseInt(sequence) || 1,
          fab_date: fabDate,
          quantity: parseInt(quantity),
          purity,
          expiry_months: parseInt(expiryMonths) || 24,
        })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setResult(data);
        if (onGenerated) onGenerated();
      } else {
        setError(data.detail || data.message || 'Generation failed');
      }
    } catch {
      setError('Connection error');
    }
    setGenerating(false);
  };

  const downloadExcel = () => {
    if (!result) return;
    const rows = result.codes.map(c => {
      const line1 = c.code.slice(0, -6);
      const line2 = c.code.slice(-6);
      return {
        'Fab. Date': result.fab_date,
        'Batch ID': result.batch_number,
        'Expiry': result.expiry_date,
        'Product': productName,
        'Code': c.code,
        'Code Line 1': line1,
        'Code Line 2': line2,
        'Code (2 lines)': `${line1}\n${line2}`,
        'Verification URL (QR)': c.url,
      };
    });
    const ws = XLSX.utils.json_to_sheet(rows);
    ws['!cols'] = [{ wch: 11 }, { wch: 20 }, { wch: 11 }, { wch: 22 }, { wch: 18 }, { wch: 12 }, { wch: 9 }, { wch: 14 }, { wch: 48 }];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Codes');
    XLSX.writeFile(wb, `${result.batch_number}_codes.xlsx`);
  };

  const inputCls = "w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500";

  return (
    <form onSubmit={handleGenerate} className="space-y-6" data-testid="generate-codes-form">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-gray-400 text-sm mb-2">Product</label>
          <select
            value={productId}
            onChange={(e) => {
              setProductId(e.target.value);
              const prod = products.find(p => p.id === e.target.value);
              if (prod) setProductName(prod.name);
              setResult(null);
            }}
            className={inputCls}
            data-testid="generate-product-select"
          >
            <option value="">Select a product</option>
            {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          {suggestion?.found && (
            <p className="text-emerald-400 text-xs mt-1" data-testid="batch-suggestion-note">
              Last batch: {suggestion.last_batch} → suggested next sequence: {suggestion.next_sequence}
            </p>
          )}
        </div>
        <div>
          <label className="block text-gray-400 text-sm mb-2">Fabrication Date</label>
          <input type="date" value={fabDate} onChange={(e) => setFabDate(e.target.value)} className={inputCls} data-testid="generate-fab-date" />
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <label className="block text-gray-400 text-sm mb-2">Product Code</label>
          <input type="text" value={productCode} onChange={(e) => setProductCode(e.target.value.toUpperCase())} placeholder="e.g. RT10" className={inputCls} data-testid="generate-product-code" />
        </div>
        <div>
          <label className="block text-gray-400 text-sm mb-2">Sequence</label>
          <input type="number" min="1" value={sequence} onChange={(e) => setSequence(e.target.value)} className={inputCls} data-testid="generate-sequence" />
        </div>
        <div>
          <label className="block text-gray-400 text-sm mb-2">Quantity</label>
          <input type="number" min="1" max="5000" value={quantity} onChange={(e) => setQuantity(e.target.value)} className={inputCls} data-testid="generate-quantity" />
        </div>
        <div>
          <label className="block text-gray-400 text-sm mb-2">Purity</label>
          <input type="text" value={purity} onChange={(e) => setPurity(e.target.value)} className={inputCls} data-testid="generate-purity" />
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <label className="block text-gray-400 text-sm mb-2">Expiry (months after fab.)</label>
          <select value={expiryMonths} onChange={(e) => setExpiryMonths(e.target.value)} className={inputCls} data-testid="generate-expiry-months">
            {EXPIRY_OPTIONS.map(m => <option key={m} value={m}>{m} months</option>)}
          </select>
          <p className="text-gray-500 text-xs mt-1">Vials: 24 • Pens (liquid): shorter shelf life</p>
        </div>
      </div>

      {batchPreview && (
        <div className="bg-gray-900/60 border border-blue-500/30 rounded-lg p-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-sm" data-testid="generate-preview">
          <div><span className="text-gray-500">Batch ID:</span> <span className="text-blue-400 font-mono">{batchPreview}</span></div>
          <div><span className="text-gray-500">Code format:</span> <span className="text-blue-400 font-mono">{codePreview}</span></div>
          <div><span className="text-gray-500">Expiry (+{parseInt(expiryMonths) || 24}mo):</span> <span className="text-blue-400 font-mono">{expiryPreview}</span></div>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-lg border bg-red-900/50 border-red-500 text-red-400" data-testid="generate-error">{error}</div>
      )}

      {result && (
        <div className="p-4 rounded-lg border bg-green-900/50 border-green-500" data-testid="generate-result">
          <p className="text-green-400 font-medium">✅ {result.generated} codes generated — batch <span className="font-mono">{result.batch_number}</span></p>
          <p className="text-green-300/70 text-sm mt-1">Expiry: {result.expiry_date} • Sample: <span className="font-mono">{result.codes[0]?.code}</span></p>
          <button type="button" onClick={downloadExcel} className="mt-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-5 py-2.5 rounded-lg transition" data-testid="download-csv-btn">
            ⬇️ Download Excel ({result.generated} codes + QR URLs)
          </button>
        </div>
      )}

      <button type="submit" disabled={generating} className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition disabled:opacity-50" data-testid="generate-submit-btn">
        {generating ? 'Generating...' : '⚡ Generate Codes'}
      </button>
    </form>
  );
}

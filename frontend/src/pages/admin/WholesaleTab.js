import React, { useState, useEffect, useMemo } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function WholesaleTab({ adminPassword }) {
  const [subTab, setSubTab] = useState('pricelist'); // 'pricelist' | 'invoice'

  return (
    <div className="space-y-6" data-testid="wholesale-tab">
      {/* Sub-tab nav */}
      <div className="flex gap-2 border-b border-gray-700">
        <button
          type="button"
          onClick={() => setSubTab('pricelist')}
          data-testid="wholesale-subtab-pricelist"
          className={`px-5 py-3 font-semibold transition border-b-2 ${
            subTab === 'pricelist'
              ? 'border-amber-500 text-amber-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          Price List
        </button>
        <button
          type="button"
          onClick={() => setSubTab('invoice')}
          data-testid="wholesale-subtab-invoice"
          className={`px-5 py-3 font-semibold transition border-b-2 ${
            subTab === 'invoice'
              ? 'border-amber-500 text-amber-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          Invoice / Order
        </button>
      </div>

      {subTab === 'pricelist' ? (
        <PriceListSection adminPassword={adminPassword} />
      ) : (
        <InvoiceSection adminPassword={adminPassword} />
      )}
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════════
   PRICE LIST SECTION
   ════════════════════════════════════════════════════════════════════ */
function PriceListSection({ adminPassword }) {
  const [customerName, setCustomerName] = useState('');
  const [company, setCompany] = useState('');
  const [email, setEmail] = useState('');
  const [tier1, setTier1] = useState(30);
  const [tier2, setTier2] = useState(35);
  const [tier3, setTier3] = useState(40);
  const [validDays, setValidDays] = useState(30);
  const [includeComingSoon, setIncludeComingSoon] = useState(false);
  const [includeOutOfStock, setIncludeOutOfStock] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);

  // Product selection
  const [selectionMode, setSelectionMode] = useState('all'); // 'all' | 'custom'
  const [products, setProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [productSearch, setProductSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState(new Set());

  useEffect(() => {
    if (selectionMode === 'custom' && products.length === 0 && !loadingProducts) {
      setLoadingProducts(true);
      fetch(`${API_URL}/api/products`)
        .then((r) => r.ok ? r.json() : [])
        .then((data) => setProducts(data || []))
        .catch(() => {})
        .finally(() => setLoadingProducts(false));
    }
    /* eslint-disable-next-line */
  }, [selectionMode]);

  const filteredProducts = useMemo(() => {
    const q = productSearch.trim().toLowerCase();
    if (!q) return products;
    return products.filter((p) =>
      (p.name || '').toLowerCase().includes(q) ||
      (p.category || '').toLowerCase().includes(q)
    );
  }, [products, productSearch]);

  const toggleProduct = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };
  const selectAllFiltered = () => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      filteredProducts.forEach((p) => next.add(p.id));
      return next;
    });
  };
  const clearSelection = () => setSelectedIds(new Set());

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/wholesale/history?limit=20`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history || []);
      }
    } catch (e) { /* ignore */ }
  };

  useEffect(() => { fetchHistory(); /* eslint-disable-next-line */ }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    setError('');
    try {
      const payload = {
        customer_name: customerName || null,
        company: company || null,
        email: email || null,
        tier_1_pct: parseFloat(tier1) || 0,
        tier_2_pct: parseFloat(tier2) || 0,
        tier_3_pct: parseFloat(tier3) || 0,
        valid_days: parseInt(validDays, 10) || 30,
        include_coming_soon: includeComingSoon,
        include_out_of_stock: includeOutOfStock,
        product_ids: selectionMode === 'custom' ? Array.from(selectedIds) : null,
      };
      if (selectionMode === 'custom' && selectedIds.size === 0) {
        setError('Select at least one product or switch to "All products".');
        setGenerating(false);
        return;
      }
      const res = await fetch(`${API_URL}/api/admin/wholesale/generate-pdf`, {
        method: 'POST',
        headers: {
          'X-Admin-Password': adminPassword,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Failed to generate (HTTP ${res.status})`);
      const blob = await res.blob();
      const cd = res.headers.get('Content-Disposition') || '';
      const match = cd.match(/filename="?([^"]+)"?/);
      const filename = match ? match[1] : `Zurix_Wholesale_${Date.now()}.pdf`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      fetchHistory();
    } catch (e) {
      setError(e.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const fmtTs = (iso) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('en-US', {
        year: 'numeric', month: 'short', day: '2-digit',
        hour: '2-digit', minute: '2-digit',
      });
    } catch { return iso.slice(0, 16); }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-1">Generate Wholesale Price List</h2>
        <p className="text-sm text-gray-400 mb-6">
          Branded PDF with retail price + 3 discount tiers by order value. All percentages are manual.
        </p>

        <form onSubmit={handleGenerate} className="space-y-5">
          <fieldset className="border border-gray-700 rounded-xl p-4">
            <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Customer (optional)</legend>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Name</label>
                <input
                  type="text" value={customerName} onChange={(e) => setCustomerName(e.target.value)}
                  placeholder="Maria Silva"
                  data-testid="wholesale-customer-name"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Company</label>
                <input
                  type="text" value={company} onChange={(e) => setCompany(e.target.value)}
                  placeholder="Med Distribuidora"
                  data-testid="wholesale-company"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Email</label>
                <input
                  type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="maria@example.com"
                  data-testid="wholesale-email"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </fieldset>

          <fieldset className="border border-gray-700 rounded-xl p-4">
            <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Discount tiers by order value (manual)</legend>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <TierInput label="Tier 1 — Orders ≤ $1,000" value={tier1} setter={setTier1} testid="wholesale-tier1" />
              <TierInput label="Tier 2 — Orders $1,001 – $1,999" value={tier2} setter={setTier2} testid="wholesale-tier2" />
              <TierInput label="Tier 3 — Orders ≥ $2,000" value={tier3} setter={setTier3} testid="wholesale-tier3" />
            </div>
          </fieldset>

          <fieldset className="border border-gray-700 rounded-xl p-4">
            <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Products in list</legend>
            <div className="flex flex-wrap gap-2 mb-3">
              <button
                type="button"
                onClick={() => setSelectionMode('all')}
                data-testid="pricelist-mode-all"
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                  selectionMode === 'all'
                    ? 'bg-amber-500 text-gray-900'
                    : 'bg-gray-900 text-gray-300 border border-gray-700 hover:border-amber-500/50'
                }`}
              >
                All products
              </button>
              <button
                type="button"
                onClick={() => setSelectionMode('custom')}
                data-testid="pricelist-mode-custom"
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                  selectionMode === 'custom'
                    ? 'bg-amber-500 text-gray-900'
                    : 'bg-gray-900 text-gray-300 border border-gray-700 hover:border-amber-500/50'
                }`}
              >
                Choose specific products
                {selectionMode === 'custom' && selectedIds.size > 0 && (
                  <span className="ml-2 px-2 py-0.5 bg-gray-900/40 rounded text-xs">{selectedIds.size}</span>
                )}
              </button>
            </div>

            {selectionMode === 'custom' && (
              <div className="space-y-3">
                <div className="flex flex-wrap items-center gap-2">
                  <input
                    type="text" value={productSearch} onChange={(e) => setProductSearch(e.target.value)}
                    placeholder="Search product..."
                    data-testid="pricelist-product-search"
                    className="flex-1 min-w-[200px] px-3 py-1.5 bg-gray-900 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                  <button type="button" onClick={selectAllFiltered}
                    data-testid="pricelist-select-all"
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition">
                    Select all{productSearch ? ' (filtered)' : ''}
                  </button>
                  <button type="button" onClick={clearSelection}
                    data-testid="pricelist-clear"
                    className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold rounded-lg transition">
                    Clear ({selectedIds.size})
                  </button>
                </div>

                {loadingProducts ? (
                  <p className="text-gray-400 text-sm">Loading products...</p>
                ) : (
                  <div className="max-h-72 overflow-y-auto border border-gray-700 rounded-lg" data-testid="pricelist-product-list">
                    {filteredProducts.length === 0 ? (
                      <p className="px-4 py-6 text-center text-gray-500 text-sm">No products match search.</p>
                    ) : (
                      <ul className="divide-y divide-gray-700">
                        {filteredProducts.map((p) => {
                          const checked = selectedIds.has(p.id);
                          return (
                            <li key={p.id} className={`flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-gray-700/30 ${checked ? 'bg-amber-500/10' : ''}`}
                              onClick={() => toggleProduct(p.id)}>
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={() => toggleProduct(p.id)}
                                onClick={(e) => e.stopPropagation()}
                                data-testid={`pricelist-check-${p.id}`}
                                className="w-4 h-4 accent-amber-500"
                              />
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className="text-gray-200 text-sm truncate">{p.name}</span>
                                  {p.coming_soon && <span className="text-[10px] px-1.5 py-0.5 bg-blue-900/60 text-blue-300 rounded">SOON</span>}
                                  {p.out_of_stock && <span className="text-[10px] px-1.5 py-0.5 bg-red-900/60 text-red-300 rounded">OOS</span>}
                                </div>
                                <div className="text-xs text-gray-500">{p.category || ''}</div>
                              </div>
                              <span className="text-xs font-mono text-gray-400">${parseFloat(p.price || 0).toFixed(2)}</span>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                )}
                <p className="text-xs text-gray-500">
                  {selectedIds.size === 0
                    ? 'No products selected. Click items above to include them in the PDF.'
                    : `${selectedIds.size} product(s) will be included in the price list.`}
                </p>
              </div>
            )}
          </fieldset>

          <fieldset className="border border-gray-700 rounded-xl p-4">
            <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Options</legend>
            <div className="flex flex-wrap gap-6 items-center">
              <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                <input type="checkbox" checked={includeComingSoon} onChange={(e) => setIncludeComingSoon(e.target.checked)}
                  data-testid="wholesale-include-coming-soon" className="w-4 h-4 accent-blue-600" />
                <span className="text-sm">Include Coming Soon products</span>
              </label>
              <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                <input type="checkbox" checked={includeOutOfStock} onChange={(e) => setIncludeOutOfStock(e.target.checked)}
                  data-testid="wholesale-include-oos" className="w-4 h-4 accent-blue-600" />
                <span className="text-sm">Include Out of Stock</span>
              </label>
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-300">Valid for</label>
                <input type="number" min="1" max="365" value={validDays} onChange={(e) => setValidDays(e.target.value)}
                  data-testid="wholesale-valid-days"
                  className="w-20 px-2 py-1 bg-gray-900 border border-gray-700 rounded text-white text-center focus:outline-none focus:border-blue-500" />
                <span className="text-sm text-gray-300">days</span>
              </div>
            </div>
          </fieldset>

          {error && (
            <div className="bg-red-900/40 border border-red-700 text-red-200 px-4 py-3 rounded-lg" data-testid="wholesale-error">
              {error}
            </div>
          )}

          <button
            type="submit" disabled={generating}
            data-testid="wholesale-generate-btn"
            className="w-full px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-lg rounded-xl transition shadow-lg"
          >
            {generating ? 'Generating PDF...' : 'Generate Wholesale PDF'}
          </button>
        </form>
      </div>

      <HistoryTable
        title="Price List History"
        rows={history}
        emptyMsg="No PDFs generated yet. Fill the form above and click Generate."
        testIdPrefix="wholesale-row"
        emptyTestId="wholesale-empty-history"
        renderRow={(h) => (
          <tr key={h.id} className="text-gray-200 hover:bg-gray-700/40 transition" data-testid={`wholesale-row-${h.reference}`}>
            <td className="px-4 py-3 font-mono text-xs">{h.reference}</td>
            <td className="px-4 py-3">{h.customer_name || h.company || '—'}</td>
            <td className="px-4 py-3 text-xs">{h.email || '—'}</td>
            <td className="px-4 py-3 text-center font-mono text-xs">{h.tier_1_pct}% / {h.tier_2_pct}% / {h.tier_3_pct}%</td>
            <td className="px-4 py-3 text-center">{h.product_count}</td>
            <td className="px-4 py-3 text-xs text-gray-400">{fmtTs(h.generated_at)}</td>
          </tr>
        )}
        headers={['Reference', 'Customer', 'Email', 'Tiers (1/2/3)', 'Products', 'Generated']}
      />
    </div>
  );
}

function TierInput({ label, value, setter, testid }) {
  return (
    <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <div className="flex items-center gap-2">
        <input
          type="number" min="0" max="99" step="0.1"
          value={value} onChange={(e) => setter(e.target.value)}
          data-testid={testid}
          className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white text-center font-bold text-lg focus:outline-none focus:border-blue-500"
        />
        <span className="text-2xl text-amber-400 font-bold">%</span>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════════
   INVOICE / ORDER SECTION
   ════════════════════════════════════════════════════════════════════ */
function InvoiceSection({ adminPassword }) {
  const [products, setProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [search, setSearch] = useState('');
  const [cart, setCart] = useState({}); // { product_id: qty }

  const [customerName, setCustomerName] = useState('');
  const [company, setCompany] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [notes, setNotes] = useState('');

  const [tier1, setTier1] = useState(30);
  const [tier2, setTier2] = useState(35);
  const [tier3, setTier3] = useState(40);
  const [useOverride, setUseOverride] = useState(false);
  const [overridePct, setOverridePct] = useState(40);

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/products`);
        if (res.ok) {
          const data = await res.json();
          setProducts(data || []);
        }
      } catch (e) { /* ignore */ }
      finally { setLoadingProducts(false); }
    })();
    fetchInvoices();
    /* eslint-disable-next-line */
  }, []);

  const fetchInvoices = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/wholesale/invoices?limit=20`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (res.ok) {
        const data = await res.json();
        setInvoices(data.invoices || []);
      }
    } catch (e) { /* ignore */ }
  };

  const filteredProducts = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return products;
    return products.filter((p) =>
      (p.name || '').toLowerCase().includes(q) ||
      (p.category || '').toLowerCase().includes(q)
    );
  }, [products, search]);

  const setQty = (id, qty) => {
    setCart((prev) => {
      const next = { ...prev };
      const n = parseInt(qty, 10);
      if (!n || n <= 0) delete next[id];
      else next[id] = n;
      return next;
    });
  };

  const cartItems = useMemo(() => {
    return Object.entries(cart).map(([id, qty]) => {
      const p = products.find((x) => x.id === id);
      const unit = parseFloat((p && p.price) || 0);
      return {
        product_id: id,
        name: (p && p.name) || id,
        qty,
        unit_price: unit,
        line_total: unit * qty,
      };
    });
  }, [cart, products]);

  const subtotal = useMemo(
    () => cartItems.reduce((s, it) => s + it.line_total, 0),
    [cartItems],
  );

  const { tierLabel, discountPct } = useMemo(() => {
    if (useOverride) {
      return { tierLabel: 'Custom Discount', discountPct: parseFloat(overridePct) || 0 };
    }
    if (subtotal <= 1000) return { tierLabel: 'Tier 1 (≤ $1,000)', discountPct: parseFloat(tier1) || 0 };
    if (subtotal < 2000) return { tierLabel: 'Tier 2 ($1,001 – $1,999)', discountPct: parseFloat(tier2) || 0 };
    return { tierLabel: 'Tier 3 (≥ $2,000)', discountPct: parseFloat(tier3) || 0 };
  }, [subtotal, useOverride, overridePct, tier1, tier2, tier3]);

  const discountValue = subtotal * (discountPct / 100);
  const total = subtotal - discountValue;

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError('');
    if (!customerName.trim()) { setError('Customer name is required.'); return; }
    if (cartItems.length === 0) { setError('Add at least one product to the invoice.'); return; }

    setGenerating(true);
    try {
      const payload = {
        customer_name: customerName.trim(),
        company: company || null,
        email: email || null,
        phone: phone || null,
        address: address || null,
        notes: notes || null,
        items: cartItems.map((it) => ({ product_id: it.product_id, quantity: it.qty })),
        tier_1_pct: parseFloat(tier1) || 0,
        tier_2_pct: parseFloat(tier2) || 0,
        tier_3_pct: parseFloat(tier3) || 0,
        override_discount_pct: useOverride ? (parseFloat(overridePct) || 0) : null,
      };
      const res = await fetch(`${API_URL}/api/admin/wholesale/generate-invoice`, {
        method: 'POST',
        headers: {
          'X-Admin-Password': adminPassword,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Failed (HTTP ${res.status}): ${txt.slice(0, 120)}`);
      }
      const blob = await res.blob();
      const cd = res.headers.get('Content-Disposition') || '';
      const match = cd.match(/filename="?([^"]+)"?/);
      const filename = match ? match[1] : `Zurix_Invoice_${Date.now()}.pdf`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      fetchInvoices();
    } catch (e) {
      setError(e.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const fmt = (v) => `$${(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const fmtTs = (iso) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('en-US', {
        year: 'numeric', month: 'short', day: '2-digit',
        hour: '2-digit', minute: '2-digit',
      });
    } catch { return iso.slice(0, 16); }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-1">Generate Wholesale Invoice</h2>
        <p className="text-sm text-gray-400 mb-6">
          Select products and quantities. Discount tier is applied automatically by subtotal — or override manually.
        </p>

        <form onSubmit={handleGenerate} className="space-y-5">
          {/* Customer */}
          <fieldset className="border border-gray-700 rounded-xl p-4">
            <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Bill To</legend>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Name *</label>
                <input type="text" required value={customerName} onChange={(e) => setCustomerName(e.target.value)}
                  placeholder="Maria Silva" data-testid="invoice-customer-name"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Company</label>
                <input type="text" value={company} onChange={(e) => setCompany(e.target.value)}
                  placeholder="Med Distribuidora" data-testid="invoice-company"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="maria@example.com" data-testid="invoice-email"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Phone</label>
                <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)}
                  placeholder="+55 11 99999-9999" data-testid="invoice-phone"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs text-gray-400 uppercase mb-1">Address</label>
                <textarea rows={2} value={address} onChange={(e) => setAddress(e.target.value)}
                  placeholder="Street, City, State, ZIP, Country" data-testid="invoice-address"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
              </div>
            </div>
          </fieldset>

          {/* Product selection */}
          <fieldset className="border border-gray-700 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Items</legend>
              <input
                type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                placeholder="Search product..." data-testid="invoice-product-search"
                className="px-3 py-1.5 bg-gray-900 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            {loadingProducts ? (
              <p className="text-gray-400 text-sm">Loading products...</p>
            ) : (
              <div className="max-h-96 overflow-y-auto border border-gray-700 rounded-lg" data-testid="invoice-product-list">
                <table className="w-full text-sm">
                  <thead className="bg-gray-900/80 text-gray-400 uppercase text-xs sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left">Product</th>
                      <th className="px-3 py-2 text-right w-24">Price</th>
                      <th className="px-3 py-2 text-center w-28">Qty</th>
                      <th className="px-3 py-2 text-right w-28">Line Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {filteredProducts.map((p) => {
                      const qty = cart[p.id] || 0;
                      const price = parseFloat(p.price || 0);
                      const lineTotal = price * qty;
                      const isInactive = p.coming_soon || p.out_of_stock;
                      return (
                        <tr key={p.id} className={`text-gray-200 ${qty > 0 ? 'bg-amber-500/5' : ''}`}>
                          <td className="px-3 py-2">
                            <div className="flex items-center gap-2">
                              <span>{p.name}</span>
                              {p.coming_soon && <span className="text-[10px] px-1.5 py-0.5 bg-blue-900/60 text-blue-300 rounded">SOON</span>}
                              {p.out_of_stock && <span className="text-[10px] px-1.5 py-0.5 bg-red-900/60 text-red-300 rounded">OOS</span>}
                            </div>
                            <div className="text-xs text-gray-500">{p.category || ''}</div>
                          </td>
                          <td className="px-3 py-2 text-right font-mono text-xs">{fmt(price)}</td>
                          <td className="px-3 py-2">
                            <input
                              type="number" min="0" step="1"
                              value={qty || ''}
                              onChange={(e) => setQty(p.id, e.target.value)}
                              disabled={isInactive}
                              placeholder="0"
                              data-testid={`invoice-qty-${p.id}`}
                              className="w-20 mx-auto block px-2 py-1 bg-gray-900 border border-gray-700 rounded text-white text-center text-sm focus:outline-none focus:border-blue-500 disabled:opacity-40"
                            />
                          </td>
                          <td className="px-3 py-2 text-right font-mono text-xs">
                            {qty > 0 ? fmt(lineTotal) : '—'}
                          </td>
                        </tr>
                      );
                    })}
                    {filteredProducts.length === 0 && (
                      <tr><td colSpan={4} className="px-3 py-6 text-center text-gray-500">No products match search.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </fieldset>

          {/* Tiers + Override */}
          <fieldset className="border border-gray-700 rounded-xl p-4">
            <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Discount</legend>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <TierInput label="Tier 1 — ≤ $1,000" value={tier1} setter={setTier1} testid="invoice-tier1" />
              <TierInput label="Tier 2 — $1,001 – $1,999" value={tier2} setter={setTier2} testid="invoice-tier2" />
              <TierInput label="Tier 3 — ≥ $2,000" value={tier3} setter={setTier3} testid="invoice-tier3" />
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-4">
              <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                <input type="checkbox" checked={useOverride} onChange={(e) => setUseOverride(e.target.checked)}
                  data-testid="invoice-use-override" className="w-4 h-4 accent-blue-600" />
                <span className="text-sm">Override discount manually</span>
              </label>
              {useOverride && (
                <div className="flex items-center gap-2">
                  <input type="number" min="0" max="99" step="0.1" value={overridePct}
                    onChange={(e) => setOverridePct(e.target.value)}
                    data-testid="invoice-override-pct"
                    className="w-24 px-2 py-1 bg-gray-900 border border-gray-700 rounded text-white text-center font-bold focus:outline-none focus:border-blue-500" />
                  <span className="text-amber-400 font-bold">%</span>
                </div>
              )}
            </div>
          </fieldset>

          {/* Notes */}
          <fieldset className="border border-gray-700 rounded-xl p-4">
            <legend className="text-xs text-amber-400 uppercase tracking-wider font-semibold px-2">Notes (optional)</legend>
            <textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)}
              placeholder="Payment instructions, shipping notes, etc." data-testid="invoice-notes"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
          </fieldset>

          {/* Live summary */}
          <div className="bg-gray-900/70 rounded-xl border border-amber-500/30 p-5" data-testid="invoice-summary">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <SummaryStat label="Items" value={cartItems.length} />
              <SummaryStat label="Subtotal" value={fmt(subtotal)} />
              <SummaryStat label={`${tierLabel} — ${discountPct}% OFF`} value={`-${fmt(discountValue)}`} accent />
              <SummaryStat label="Total" value={fmt(total)} bold />
            </div>
          </div>

          {error && (
            <div className="bg-red-900/40 border border-red-700 text-red-200 px-4 py-3 rounded-lg" data-testid="invoice-error">
              {error}
            </div>
          )}

          <button
            type="submit" disabled={generating || cartItems.length === 0 || !customerName.trim()}
            data-testid="invoice-generate-btn"
            className="w-full px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-lg rounded-xl transition shadow-lg"
          >
            {generating ? 'Generating Invoice...' : 'Generate Invoice PDF'}
          </button>
        </form>
      </div>

      <HistoryTable
        title="Invoice History"
        rows={invoices}
        emptyMsg="No invoices generated yet."
        renderRow={(inv) => (
          <tr key={inv.id} className="text-gray-200 hover:bg-gray-700/40 transition" data-testid={`invoice-row-${inv.invoice_number}`}>
            <td className="px-4 py-3 font-mono text-xs">{inv.invoice_number}</td>
            <td className="px-4 py-3">{inv.customer_name || inv.company || '—'}</td>
            <td className="px-4 py-3 text-xs">{inv.email || '—'}</td>
            <td className="px-4 py-3 text-center text-xs">{(inv.items || []).length}</td>
            <td className="px-4 py-3 text-right font-mono text-xs">{fmt(inv.subtotal)}</td>
            <td className="px-4 py-3 text-center text-xs text-amber-400">{inv.discount_pct}%</td>
            <td className="px-4 py-3 text-right font-mono text-xs font-bold">{fmt(inv.total)}</td>
            <td className="px-4 py-3 text-xs text-gray-400">{fmtTs(inv.generated_at)}</td>
          </tr>
        )}
        headers={['Invoice #', 'Customer', 'Email', 'Items', 'Subtotal', 'Discount', 'Total', 'Generated']}
      />
    </div>
  );
}

function SummaryStat({ label, value, accent, bold }) {
  return (
    <div>
      <div className={`text-xs uppercase tracking-wider mb-1 ${accent ? 'text-amber-400' : 'text-gray-400'}`}>{label}</div>
      <div className={`${bold ? 'text-2xl text-amber-400' : 'text-lg text-white'} font-bold`}>{value}</div>
    </div>
  );
}

function HistoryTable({ title, rows, emptyMsg, renderRow, headers, emptyTestId }) {
  return (
    <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-700">
        <h3 className="text-lg font-bold text-white">
          {title}
          <span className="text-sm text-gray-400 font-normal ml-2">({rows.length})</span>
        </h3>
      </div>
      {rows.length === 0 ? (
        <div className="p-6 text-center text-gray-400" data-testid={emptyTestId || 'history-empty'}>
          {emptyMsg}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-900/60 text-gray-400 uppercase text-xs">
              <tr>
                {headers.map((h) => (
                  <th key={h} className={`px-4 py-3 ${h === 'Items' || h === 'Discount' ? 'text-center' : (h === 'Subtotal' || h === 'Total' ? 'text-right' : 'text-left')}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {rows.map(renderRow)}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

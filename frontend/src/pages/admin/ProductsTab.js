import React, { useState, useEffect, useMemo } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const EMPTY_FORM = {
  name: '',
  category: 'Research Peptides',
  product_type: '',
  purity: '≥99% HPLC',
  dosage: '',
  description: '',
  price: 0,
  verification_code: '',
  storage_info: 'Store lyophilized at -20°C. Stable 2-8°C for 30 days after reconstitution.',
  batch_number: '',
  manufacturing_date: '',
  expiry_date: '',
  coa_url: '',
  featured: false,
  image_url: '',
  coming_soon: false,
  out_of_stock: false,
};

export default function ProductsTab({ adminPassword }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState(null); // product being edited, or 'new'
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [qrModal, setQrModal] = useState(null); // { code, image, name }

  const loadProducts = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/products`);
      if (res.ok) setProducts(await res.json());
    } catch (e) { /* ignore */ }
    finally { setLoading(false); }
  };

  useEffect(() => { loadProducts(); }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return products;
    return products.filter((p) =>
      (p.name || '').toLowerCase().includes(q) ||
      (p.product_type || '').toLowerCase().includes(q) ||
      (p.verification_code || '').toLowerCase().includes(q)
    );
  }, [products, search]);

  const openNew = () => {
    setEditing('new');
    setForm(EMPTY_FORM);
    setError('');
    setNotice('');
  };

  const openEdit = (p) => {
    setEditing(p);
    setForm({ ...EMPTY_FORM, ...p });
    setError('');
    setNotice('');
  };

  const closeForm = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setError('');
  };

  const setField = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const isNew = editing === 'new';
      const url = isNew
        ? `${API_URL}/api/admin/products`
        : `${API_URL}/api/admin/products/${editing.id}`;
      const method = isNew ? 'POST' : 'PUT';

      const body = { ...form, price: parseFloat(form.price) || 0 };

      const res = await fetch(url, {
        method,
        headers: {
          'X-Admin-Password': adminPassword,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(`HTTP ${res.status}: ${t.slice(0, 160)}`);
      }
      setNotice(isNew ? 'Product created.' : 'Product updated.');
      closeForm();
      await loadProducts();
    } catch (e) {
      setError(e.message || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (p) => {
    if (!window.confirm(`Delete "${p.name}"? This cannot be undone.`)) return;
    try {
      const res = await fetch(`${API_URL}/api/admin/products/${p.id}`, {
        method: 'DELETE',
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setNotice(`Deleted: ${p.name}`);
      await loadProducts();
    } catch (e) {
      setError(e.message || 'Delete failed');
    }
  };

  const showQr = async (p) => {
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/admin/products/${p.id}/qr`, {
        headers: { 'X-Admin-Password': adminPassword },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setQrModal({ code: data.verification_code, image: data.qr_image, name: p.name });
    } catch (e) {
      setError(e.message || 'QR generation failed');
    }
  };

  const fmt = (v) => `$${(parseFloat(v) || 0).toFixed(2)}`;

  return (
    <div className="space-y-6" data-testid="products-tab">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-3 justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Products Catalog ({products.length})</h2>
          <p className="text-sm text-gray-400">Create, edit and generate QR codes for products shown on the storefront.</p>
        </div>
        <div className="flex gap-2">
          <input
            type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search product..."
            data-testid="products-search"
            className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            type="button" onClick={openNew}
            data-testid="products-new-btn"
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-bold rounded-lg transition"
          >
            + New product
          </button>
        </div>
      </div>

      {notice && <div className="bg-green-900/40 border border-green-700 text-green-200 px-4 py-2 rounded-lg text-sm" data-testid="products-notice">{notice}</div>}
      {error && <div className="bg-red-900/40 border border-red-700 text-red-200 px-4 py-2 rounded-lg text-sm" data-testid="products-error">{error}</div>}

      {/* Edit / Create modal */}
      {editing && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4" onClick={closeForm}>
          <div className="bg-gray-900 rounded-2xl border border-gray-700 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between sticky top-0 bg-gray-900 z-10">
              <h3 className="text-lg font-bold text-white">
                {editing === 'new' ? 'Create new product' : `Edit: ${editing.name}`}
              </h3>
              <button type="button" onClick={closeForm} className="text-gray-400 hover:text-white text-2xl leading-none" data-testid="products-form-close">×</button>
            </div>
            <form onSubmit={handleSave} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Field label="Name *" required value={form.name} onChange={(v) => setField('name', v)} testid="product-field-name" />
                <Field label="Product type *" required value={form.product_type} onChange={(v) => setField('product_type', v)} testid="product-field-type" placeholder="e.g. Epitalon" />
                <Field label="Category" value={form.category} onChange={(v) => setField('category', v)} testid="product-field-category" />
                <Field label="Dosage" value={form.dosage} onChange={(v) => setField('dosage', v)} testid="product-field-dosage" placeholder="e.g. 10mg" />
                <Field label="Purity" value={form.purity} onChange={(v) => setField('purity', v)} testid="product-field-purity" />
                <Field label="Price (USD)" type="number" step="0.01" value={form.price} onChange={(v) => setField('price', v)} testid="product-field-price" />
                <Field label="Verification code" value={form.verification_code} onChange={(v) => setField('verification_code', v)} testid="product-field-code" placeholder="Auto-generated if empty" hint="Used for QR code generation. e.g. ZX-EPIT10" />
                <Field label="Batch number" value={form.batch_number} onChange={(v) => setField('batch_number', v)} testid="product-field-batch" />
                <Field label="Manufacturing date" type="date" value={form.manufacturing_date} onChange={(v) => setField('manufacturing_date', v)} testid="product-field-mfg" />
                <Field label="Expiry date" type="date" value={form.expiry_date} onChange={(v) => setField('expiry_date', v)} testid="product-field-exp" />
                <Field label="Image URL" value={form.image_url} onChange={(v) => setField('image_url', v)} testid="product-field-image" placeholder="/api/images/products/name.png" />
                <Field label="COA URL" value={form.coa_url} onChange={(v) => setField('coa_url', v)} testid="product-field-coa" placeholder="/coa/name.pdf" />
              </div>

              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Description</label>
                <textarea rows={3} value={form.description} onChange={(e) => setField('description', e.target.value)}
                  data-testid="product-field-description"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
              </div>

              <div>
                <label className="block text-xs text-gray-400 uppercase mb-1">Storage info</label>
                <textarea rows={2} value={form.storage_info} onChange={(e) => setField('storage_info', e.target.value)}
                  data-testid="product-field-storage"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500" />
              </div>

              <div className="flex flex-wrap gap-6 pt-2">
                <Toggle label="Featured" checked={form.featured} onChange={(v) => setField('featured', v)} testid="product-toggle-featured" />
                <Toggle label="Coming soon" checked={form.coming_soon} onChange={(v) => setField('coming_soon', v)} testid="product-toggle-coming" />
                <Toggle label="Out of stock" checked={form.out_of_stock} onChange={(v) => setField('out_of_stock', v)} testid="product-toggle-oos" />
              </div>

              {error && <div className="bg-red-900/40 border border-red-700 text-red-200 px-4 py-2 rounded-lg text-sm">{error}</div>}

              <div className="flex gap-3 pt-3 border-t border-gray-700">
                <button type="submit" disabled={saving}
                  data-testid="products-form-save"
                  className="flex-1 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:opacity-50 text-white font-bold rounded-lg transition">
                  {saving ? 'Saving...' : (editing === 'new' ? 'Create product' : 'Save changes')}
                </button>
                <button type="button" onClick={closeForm} className="px-4 py-2.5 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* QR Modal */}
      {qrModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4" onClick={() => setQrModal(null)}>
          <div className="bg-gray-900 rounded-2xl border border-gray-700 max-w-md w-full p-6 text-center"
            onClick={(e) => e.stopPropagation()} data-testid="products-qr-modal">
            <h3 className="text-lg font-bold text-white mb-1">{qrModal.name}</h3>
            <p className="text-sm text-gray-400 mb-4">Verification code: <span className="font-mono text-amber-400">{qrModal.code}</span></p>
            <img src={qrModal.image} alt="QR Code" className="mx-auto bg-white p-3 rounded-lg" style={{ width: 260, height: 260 }} />
            <div className="flex gap-2 mt-4">
              <a href={qrModal.image} download={`QR_${qrModal.code}.png`}
                data-testid="products-qr-download"
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition">
                Download PNG
              </a>
              <button type="button" onClick={() => setQrModal(null)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Products list */}
      {loading ? (
        <p className="text-gray-400 text-sm">Loading products...</p>
      ) : (
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-900/60 text-gray-400 uppercase text-xs">
                <tr>
                  <th className="px-4 py-3 text-left">Product</th>
                  <th className="px-4 py-3 text-left">Type</th>
                  <th className="px-4 py-3 text-right">Price</th>
                  <th className="px-4 py-3 text-left">Verif. Code</th>
                  <th className="px-4 py-3 text-center">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filtered.length === 0 ? (
                  <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-500">No products found.</td></tr>
                ) : filtered.map((p) => (
                  <tr key={p.id} className="text-gray-200 hover:bg-gray-700/30 transition" data-testid={`product-row-${p.id}`}>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {p.image_url && (
                          <img src={p.image_url.startsWith('http') ? p.image_url : `${API_URL}${p.image_url}`}
                            alt="" className="w-8 h-8 object-contain rounded bg-gray-900" />
                        )}
                        <span className="font-medium">{p.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400">{p.product_type}</td>
                    <td className="px-4 py-3 text-right font-mono text-xs">{fmt(p.price)}</td>
                    <td className="px-4 py-3 font-mono text-xs">{p.verification_code || '—'}</td>
                    <td className="px-4 py-3 text-center">
                      {p.coming_soon && <span className="text-[10px] px-2 py-0.5 bg-blue-900/60 text-blue-300 rounded">SOON</span>}
                      {p.out_of_stock && <span className="text-[10px] px-2 py-0.5 bg-red-900/60 text-red-300 rounded ml-1">OOS</span>}
                      {!p.coming_soon && !p.out_of_stock && <span className="text-[10px] px-2 py-0.5 bg-green-900/60 text-green-300 rounded">ACTIVE</span>}
                      {p.featured && <span className="text-[10px] px-2 py-0.5 bg-amber-900/60 text-amber-300 rounded ml-1">★</span>}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-1">
                        <button type="button" onClick={() => showQr(p)}
                          data-testid={`product-qr-${p.id}`}
                          className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded transition"
                          title="Show QR code">QR</button>
                        <button type="button" onClick={() => openEdit(p)}
                          data-testid={`product-edit-${p.id}`}
                          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold rounded transition"
                          title="Edit">Edit</button>
                        <button type="button" onClick={() => handleDelete(p)}
                          data-testid={`product-delete-${p.id}`}
                          className="px-2 py-1 bg-red-700 hover:bg-red-800 text-white text-xs font-semibold rounded transition"
                          title="Delete">Del</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', required, placeholder, hint, step, testid }) {
  return (
    <div>
      <label className="block text-xs text-gray-400 uppercase mb-1">{label}</label>
      <input
        type={type} required={required} value={value ?? ''} step={step}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        data-testid={testid}
        className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
      />
      {hint && <p className="text-[10px] text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}

function Toggle({ label, checked, onChange, testid }) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)}
        data-testid={testid}
        className="w-4 h-4 accent-amber-500" />
      <span className="text-sm text-gray-300">{label}</span>
    </label>
  );
}

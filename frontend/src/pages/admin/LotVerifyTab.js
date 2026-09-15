import React, { useEffect, useState } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function LotVerifyTab({ adminPassword }) {
  const [products, setProducts] = useState([]);
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  const [productId, setProductId] = useState('');
  const [lotNumber, setLotNumber] = useState('');
  const [mfgDate, setMfgDate] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [purity, setPurity] = useState('≥99%');

  const loadProducts = async () => {
    try {
      const res = await fetch(`${API_URL}/api/products`);
      const data = await res.json();
      setProducts(data);
    } catch (e) { /* ignore */ }
  };

  const loadLots = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/lot-batches`, {
        headers: { 'x-admin-password': adminPassword },
      });
      const data = await res.json();
      setLots(data.lots || []);
    } catch (e) { /* ignore */ } finally { setLoading(false); }
  };

  useEffect(() => { loadProducts(); loadLots(); /* eslint-disable-next-line */ }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setMsg(null);
    if (!productId || !lotNumber.trim()) {
      setMsg({ type: 'error', text: 'Select a product and enter a lot number.' });
      return;
    }
    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/lot-batches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-admin-password': adminPassword },
        body: JSON.stringify({
          product_id: productId,
          lot_number: lotNumber.trim().toUpperCase(),
          manufacturing_date: mfgDate,
          expiry_date: expiryDate,
          purity: purity,
        }),
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setMsg({ type: 'success', text: data.updated ? 'Lot updated successfully.' : 'Lot registered successfully.' });
        setLotNumber('');
        setMfgDate('');
        setExpiryDate('');
        loadLots();
      } else {
        setMsg({ type: 'error', text: data.detail || 'Failed to save lot.' });
      }
    } catch (e) {
      setMsg({ type: 'error', text: 'Connection error.' });
    } finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this lot? Verifications of this lot will stop authenticating.')) return;
    try {
      await fetch(`${API_URL}/api/admin/lot-batches/${id}`, {
        method: 'DELETE',
        headers: { 'x-admin-password': adminPassword },
      });
      loadLots();
    } catch (e) { /* ignore */ }
  };

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700" data-testid="lotverify-tab">
      <h2 className="text-xl font-bold text-white mb-2">Lot Verification</h2>
      <p className="text-gray-400 text-sm mb-6">
        Register a lot number for products verified by batch (e.g. sprays). Any verification of a registered lot
        authenticates as genuine — the same lot can be verified unlimited times without a counterfeit warning.
      </p>

      <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-300 mb-1">Product</label>
          <select
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            data-testid="lotverify-product-select"
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2"
          >
            <option value="">Select a product</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-300 mb-1">Lot Number</label>
          <input
            type="text"
            value={lotNumber}
            onChange={(e) => setLotNumber(e.target.value.toUpperCase())}
            data-testid="lotverify-lot-input"
            placeholder="ZX-GHKAHK55-1"
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 font-mono"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-300 mb-1">Purity</label>
          <input
            type="text"
            value={purity}
            onChange={(e) => setPurity(e.target.value)}
            data-testid="lotverify-purity-input"
            placeholder="≥99%"
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-300 mb-1">Manufacturing Date</label>
          <input
            type="date"
            value={mfgDate}
            onChange={(e) => setMfgDate(e.target.value)}
            data-testid="lotverify-mfg-input"
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-300 mb-1">Expiry Date</label>
          <input
            type="date"
            value={expiryDate}
            onChange={(e) => setExpiryDate(e.target.value)}
            data-testid="lotverify-expiry-input"
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div className="md:col-span-2 flex items-center gap-3">
          <button
            type="submit"
            disabled={saving}
            data-testid="lotverify-save-btn"
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 text-white font-semibold px-5 py-2 rounded-lg"
          >
            {saving ? 'Saving...' : 'Register Lot'}
          </button>
          {msg && (
            <span data-testid="lotverify-msg" className={msg.type === 'success' ? 'text-green-400 text-sm' : 'text-red-400 text-sm'}>
              {msg.text}
            </span>
          )}
        </div>
      </form>

      <h3 className="text-lg font-semibold text-white mb-3">Registered Lots ({lots.length})</h3>
      {loading ? (
        <p className="text-gray-400 text-sm">Loading...</p>
      ) : lots.length === 0 ? (
        <p className="text-gray-500 text-sm">No lots registered yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm" data-testid="lotverify-table">
            <thead>
              <tr className="text-gray-400 text-left border-b border-gray-700">
                <th className="py-2 pr-4">Lot Number</th>
                <th className="py-2 pr-4">Product</th>
                <th className="py-2 pr-4">Purity</th>
                <th className="py-2 pr-4">Mfg</th>
                <th className="py-2 pr-4">Expiry</th>
                <th className="py-2 pr-4"></th>
              </tr>
            </thead>
            <tbody>
              {lots.map((lot) => (
                <tr key={lot.id} className="border-b border-gray-800 text-gray-200">
                  <td className="py-2 pr-4 font-mono text-blue-300">{lot.lot_number}</td>
                  <td className="py-2 pr-4">{lot.product_name}</td>
                  <td className="py-2 pr-4">{lot.purity || '-'}</td>
                  <td className="py-2 pr-4">{lot.manufacturing_date || '-'}</td>
                  <td className="py-2 pr-4">{lot.expiry_date || '-'}</td>
                  <td className="py-2 pr-4">
                    <button
                      onClick={() => handleDelete(lot.id)}
                      data-testid={`lotverify-delete-${lot.id}`}
                      className="text-red-400 hover:text-red-300 text-xs"
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
    </div>
  );
}

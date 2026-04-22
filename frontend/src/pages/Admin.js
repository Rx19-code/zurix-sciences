import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function Admin() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Import form
  const [productId, setProductId] = useState('');
  const [productName, setProductName] = useState('');
  const [batchNumber, setBatchNumber] = useState('');
  const [purity, setPurity] = useState('≥99%');
  const [expiryDate, setExpiryDate] = useState('');
  const [codesText, setCodesText] = useState('');
  const [importResult, setImportResult] = useState(null);
  const [lastImportBatchId, setLastImportBatchId] = useState('');
  
  // Data views
  const [products, setProducts] = useState([]);
  const [batches, setBatches] = useState([]);
  const [codes, setCodes] = useState([]);
  const [logs, setLogs] = useState([]);
  const [leads, setLeads] = useState([]);
  const [leadsTotal, setLeadsTotal] = useState(0);
  const [leadsSearch, setLeadsSearch] = useState('');
  const [leadsFilter, setLeadsFilter] = useState('');
  const [loadingLeads, setLoadingLeads] = useState(false);
  const [activeTab, setActiveTab] = useState('import');
  const [searchCode, setSearchCode] = useState('');
  const [searching, setSearching] = useState(false);
  const [codesTotal, setCodesTotal] = useState(0);
  const [hasMoreCodes, setHasMoreCodes] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  
  // Edit batch modal
  const [editingBatch, setEditingBatch] = useState(null);
  const [editPurity, setEditPurity] = useState('');
  const [editExpiryDate, setEditExpiryDate] = useState('');
  const [savingBatch, setSavingBatch] = useState(false);
  
  // Check stored password on mount
  useEffect(() => {
    const storedPassword = sessionStorage.getItem('admin_password');
    if (storedPassword) {
      setPassword(storedPassword);
      setIsLoggedIn(true);
      loadData(storedPassword);
    }
  }, []);
  
  // Search codes with debounce
  useEffect(() => {
    if (!isLoggedIn) return;
    const timer = setTimeout(async () => {
      if (searchCode.length >= 2) {
        setSearching(true);
        try {
          const res = await fetch(`${API_URL}/api/admin/codes?search=${encodeURIComponent(searchCode)}&limit=250`, {
            headers: { 'x-admin-password': password }
          });
          if (res.ok) {
            const data = await res.json();
            setCodes(data.codes || []);
            setCodesTotal(data.total_matching || 0);
            setHasMoreCodes(data.has_more || false);
          }
        } catch (err) {
          console.error('Search error:', err);
        }
        setSearching(false);
      } else if (searchCode.length === 0) {
        // Reload codes when search is cleared
        loadCodes(password, 0, true);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchCode, isLoggedIn, password]);
  
  const loadCodes = async (pwd, skip = 0, reset = false) => {
    try {
      const res = await fetch(`${API_URL}/api/admin/codes?limit=250&skip=${skip}`, {
        headers: { 'x-admin-password': pwd }
      });
      if (res.ok) {
        const data = await res.json();
        if (reset) {
          setCodes(data.codes || []);
        } else {
          setCodes(prev => [...prev, ...(data.codes || [])]);
        }
        setCodesTotal(data.total || 0);
        setHasMoreCodes(data.has_more || false);
      }
    } catch (err) {
      console.error('Error loading codes:', err);
    }
  };
  
  const loadMoreCodes = async () => {
    setLoadingMore(true);
    await loadCodes(password, codes.length, false);
    setLoadingMore(false);
  };
  
  const openEditBatch = (batch) => {
    setEditingBatch(batch._id);
    setEditPurity(batch.purity || '');
    setEditExpiryDate(batch.expiry_date || '');
  };
  
  const saveEditBatch = async () => {
    setSavingBatch(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/batch/update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-admin-password': password
        },
        body: JSON.stringify({
          batch_number: editingBatch,
          purity: editPurity || null,
          expiry_date: editExpiryDate || null
        })
      });
      const data = await res.json();
      if (res.ok) {
        alert(`Updated ${data.updated} codes!`);
        setEditingBatch(null);
        loadData(password); // Reload data
      } else {
        alert(data.detail || 'Error updating batch');
      }
    } catch (err) {
      alert('Error: ' + err.message);
    }
    setSavingBatch(false);
  };
  
  const loadData = async (pwd) => {
    try {
      // Load products
      const prodRes = await fetch(`${API_URL}/api/products`);
      const prodData = await prodRes.json();
      setProducts(prodData || []);
      
      // Load batches
      const batchRes = await fetch(`${API_URL}/api/admin/batches`, {
        headers: { 'x-admin-password': pwd }
      });
      if (batchRes.ok) {
        const batchData = await batchRes.json();
        setBatches(batchData.batches || []);
      }
      
      // Load codes with pagination (only first 100)
      await loadCodes(pwd, 0, true);
      
      // Load logs
      const logsRes = await fetch(`${API_URL}/api/admin/verification-logs?limit=50`, {
        headers: { 'x-admin-password': pwd }
      });
      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData.logs || []);
      }
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };
  
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch(`${API_URL}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });
      
      if (res.ok) {
        sessionStorage.setItem('admin_password', password);
        setIsLoggedIn(true);
        loadData(password);
      } else {
        setError('Invalid password');
      }
    } catch (err) {
      setError('Connection error');
    }
    setLoading(false);
  };
  
  const handleLogout = () => {
    sessionStorage.removeItem('admin_password');
    setIsLoggedIn(false);
    setPassword('');
  };
  
  const handleImport = async (e) => {
    e.preventDefault();
    setLoading(true);
    setImportResult(null);
    
    const codes = codesText.split('\n').map(c => c.trim()).filter(c => c);
    
    if (!productId || !productName || !batchNumber || codes.length === 0) {
      setImportResult({ success: false, message: 'Please fill all fields' });
      setLoading(false);
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/admin/import-codes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-admin-password': password
        },
        body: JSON.stringify({
          product_id: productId,
          product_name: productName,
          batch_number: batchNumber,
          purity: purity,
          expiry_date: expiryDate,
          codes: codes
        })
      });
      
      const data = await res.json();
      setImportResult(data);
      
      if (data.success) {
        setCodesText('');
        if (data.import_batch_id) {
          setLastImportBatchId(data.import_batch_id);
        }
        loadData(password);
      }
    } catch (err) {
      setImportResult({ success: false, message: 'Connection error' });
    }
    setLoading(false);
  };
  
  const handleDeleteBatch = async (batchNumber) => {
    if (!window.confirm(`Are you sure you want to delete all codes for batch ${batchNumber}?`)) {
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/admin/batch/${batchNumber}`, {
        method: 'DELETE',
        headers: { 'x-admin-password': password }
      });
      
      if (res.ok) {
        loadData(password);
      }
    } catch (err) {
      alert('Error deleting batch');
    }
  };

  const handleResetBatch = async (batchNumber) => {
    if (!window.confirm(`Reset all verifications for batch ${batchNumber}? Codes will NOT be deleted.`)) {
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/admin/reset-verifications`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-admin-password': password },
        body: JSON.stringify({ batch_number: batchNumber })
      });
      
      const data = await res.json();
      if (data.success) {
        alert(`Reset ${data.reset_count} codes in batch ${batchNumber}`);
        loadData(password);
      }
    } catch (err) {
      alert('Error resetting verifications');
    }
  };

  const handleResetCode = async (code) => {
    if (!window.confirm(`Reset verifications for code ${code}?`)) {
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/admin/reset-verifications`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-admin-password': password },
        body: JSON.stringify({ code: code })
      });
      
      const data = await res.json();
      if (data.success) {
        loadData(password);
      }
    } catch (err) {
      alert('Error resetting code');
    }
  };
  
  const handleDeleteCode = async (code) => {
    if (!window.confirm(`Delete code ${code}?`)) {
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/admin/code/${encodeURIComponent(code)}`, {
        method: 'DELETE',
        headers: { 'x-admin-password': password }
      });
      
      if (res.ok) {
        loadData(password);
      } else {
        alert('Error deleting code');
      }
    } catch (err) {
      alert('Error deleting code');
    }
  };
  
  // Load leads
  const loadLeads = async (pwd, search = '', filter = '') => {
    setLoadingLeads(true);
    try {
      let url = `${API_URL}/api/admin/leads?limit=200`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (filter) url += `&protocol_id=${encodeURIComponent(filter)}`;
      const res = await fetch(url, { headers: { 'x-admin-password': pwd } });
      if (res.ok) {
        const data = await res.json();
        setLeads(data.leads || []);
        setLeadsTotal(data.total || 0);
      }
    } catch (err) {
      console.error('Error loading leads:', err);
    }
    setLoadingLeads(false);
  };

  // Leads search debounce
  useEffect(() => {
    if (!isLoggedIn || activeTab !== 'leads') return;
    const timer = setTimeout(() => {
      loadLeads(password, leadsSearch, leadsFilter);
    }, 300);
    return () => clearTimeout(timer);
  }, [leadsSearch, leadsFilter, activeTab, isLoggedIn]);

  const exportLeadsCSV = () => {
    let url = `${API_URL}/api/admin/leads/export`;
    if (leadsFilter) url += `?protocol_id=${encodeURIComponent(leadsFilter)}`;
    // Need to add header - use fetch + blob
    fetch(url, { headers: { 'x-admin-password': password } })
      .then(res => res.blob())
      .then(blob => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'zurix_leads.csv';
        link.click();
      })
      .catch(err => alert('Export error: ' + err.message));
  };

  // Use codes directly since search is server-side now
  const [codeFilter, setCodeFilter] = useState('all');
  const filteredCodes = codeFilter === 'all' ? codes : codeFilter === 'verified' ? codes.filter(c => c.verification_count > 0) : codes.filter(c => c.verification_count === 0);
  
  // Login screen
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-gray-800 rounded-2xl p-8 w-full max-w-md border border-gray-700">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-white">Admin Access</h1>
            <p className="text-gray-400 mt-2">Zurix Sciences</p>
          </div>
          
          <form onSubmit={handleLogin}>
            <div className="mb-6">
              <label className="block text-gray-400 text-sm mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                placeholder="Enter admin password"
              />
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    );
  }
  
  // Admin dashboard
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-white font-bold">Admin Panel</h1>
              <p className="text-gray-400 text-sm">Zurix Sciences</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-gray-400 hover:text-white text-sm"
          >
            Logout
          </button>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex gap-2 mb-6">
          {[
            { id: 'import', label: 'Import Codes', icon: '📥' },
            { id: 'labels', label: 'Labels', icon: '🏷️' },
            { id: 'codes', label: 'All Codes', icon: '🔑' },
            { id: 'batches', label: 'Batches', icon: '📦' },
            { id: 'leads', label: 'Leads', icon: '📊' },
            { id: 'logs', label: 'Verification Logs', icon: '📋' },
            { id: 'email', label: 'Email', icon: '✉️' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
        
        {/* Import Tab */}
        {activeTab === 'import' && (
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-6">Import Verification Codes</h2>
            
            <form onSubmit={handleImport} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Product</label>
                  <select
                    value={productId}
                    onChange={(e) => {
                      setProductId(e.target.value);
                      const prod = products.find(p => p.id === e.target.value);
                      if (prod) setProductName(prod.name);
                    }}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="">Select a product</option>
                    {products.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Batch Number</label>
                  <input
                    type="text"
                    value={batchNumber}
                    onChange={(e) => setBatchNumber(e.target.value.toUpperCase())}
                    placeholder="e.g. ZX-261216-RT10-1"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Purity</label>
                  <input
                    type="text"
                    value={purity}
                    onChange={(e) => setPurity(e.target.value)}
                    placeholder="e.g. ≥99%"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Expiry Date</label>
                  <input
                    type="date"
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">
                  Codes (one per line)
                </label>
                <textarea
                  value={codesText}
                  onChange={(e) => setCodesText(e.target.value)}
                  placeholder="ZX-261216-RT10-1-00038A&#10;ZX-261216-RT10-1-000659&#10;ZX-261216-RT10-1-000A2A"
                  rows={10}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-blue-500"
                />
                <p className="text-gray-500 text-sm mt-2">
                  {codesText.split('\n').filter(c => c.trim()).length} codes entered
                </p>
              </div>
              
              {importResult && (
                <div className={`p-4 rounded-lg border ${
                  importResult.success 
                    ? 'bg-green-900/50 border-green-500 text-green-400'
                    : 'bg-red-900/50 border-red-500 text-red-400'
                }`}>
                  <p className="font-medium">{importResult.message}</p>
                  {importResult.imported !== undefined && (
                    <p className="text-sm mt-1">
                      Imported: {importResult.imported} | Duplicates skipped: {importResult.duplicates}
                    </p>
                  )}
                </div>
              )}
              
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition disabled:opacity-50"
              >
                {loading ? 'Importing...' : 'Import Codes'}
              </button>
            </form>
          </div>
        )}
        
        {/* Labels Tab */}
        {activeTab === 'labels' && (
          <LabelsTab password={password} apiUrl={API_URL} codes={codes} batches={batches} lastImportBatchId={lastImportBatchId} />
        )}
        
        {/* Codes Tab */}
        {activeTab === 'codes' && (
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">
                All Codes ({filteredCodes.length} of {codesTotal})
                {searching && <span className="ml-2 text-blue-400 text-sm">Searching...</span>}
              </h2>
              <div className="flex items-center gap-3">
                <div className="flex gap-1">
                  {[
                    { id: 'all', label: 'All' },
                    { id: 'verified', label: 'Verified' },
                    { id: 'new', label: 'New' },
                  ].map(function(f) {
                    return (
                      <button key={f.id} onClick={function() { setCodeFilter(f.id); }}
                        className={'px-3 py-1 rounded text-xs font-medium transition ' + (codeFilter === f.id ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400 hover:text-white')}>
                        {f.label}
                      </button>
                    );
                  })}
                </div>
                <input
                  type="text"
                  value={searchCode}
                  onChange={(e) => setSearchCode(e.target.value)}
                  placeholder="Search code, product or batch..."
                  className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-blue-500 w-72"
                />
              </div>
            </div>
            
            {filteredCodes.length === 0 ? (
              <p className="text-gray-400">{searching ? 'Searching...' : 'No codes found'}</p>
            ) : (
              <>
                <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
                  <table className="w-full">
                    <thead className="sticky top-0 bg-gray-800">
                      <tr className="text-left text-gray-400 border-b border-gray-700">
                        <th className="pb-3 font-medium">Code</th>
                        <th className="pb-3 font-medium">Product</th>
                        <th className="pb-3 font-medium">Batch</th>
                        <th className="pb-3 font-medium">Scans</th>
                        <th className="pb-3 font-medium">Status</th>
                        <th className="pb-3 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                    {filteredCodes.map((code, i) => (
                      <tr key={i} className="border-b border-gray-700/50">
                        <td className="py-3 text-white font-mono text-sm">{code.code}</td>
                        <td className="py-3 text-gray-300 text-sm">{code.product_name}</td>
                        <td className="py-3 text-gray-400 text-sm">{code.batch_number}</td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded text-sm ${
                            code.verification_count === 0 
                              ? 'bg-gray-700 text-gray-400'
                              : code.verification_count === 1
                                ? 'bg-green-900/50 text-green-400'
                                : code.verification_count === 2
                                  ? 'bg-yellow-900/50 text-yellow-400'
                                  : 'bg-red-900/50 text-red-400'
                          }`}>
                            {code.verification_count}
                          </span>
                        </td>
                        <td className="py-3">
                          {code.verification_count >= 4 ? (
                            <span className="text-red-400 text-sm">High Risk</span>
                          ) : code.verification_count === 3 ? (
                            <span className="text-yellow-400 text-sm">Caution</span>
                          ) : code.verification_count > 0 ? (
                            <span className="text-green-400 text-sm">Verified</span>
                          ) : (
                            <span className="text-gray-400 text-sm">New</span>
                          )}
                        </td>
                        <td className="py-3 space-x-1">
                          {code.verification_count > 0 && (
                            <button
                              onClick={() => handleResetCode(code.code)}
                              className="text-yellow-400 hover:text-yellow-300 text-sm px-2 py-1 hover:bg-yellow-900/30 rounded"
                            >
                              Reset
                            </button>
                          )}
                          <button
                            onClick={() => handleDeleteCode(code.code)}
                            className="text-red-400 hover:text-red-300 text-sm px-2 py-1 hover:bg-red-900/30 rounded"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                </div>
                
                {/* Load More Button */}
                {hasMoreCodes && !searchCode && (
                  <div className="mt-4 text-center">
                    <button
                      onClick={loadMoreCodes}
                      disabled={loadingMore}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-semibold px-6 py-2 rounded-lg transition"
                    >
                      {loadingMore ? 'Loading...' : `Load More (${codesTotal - codes.length} remaining)`}
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}
        
        {/* Batches Tab */}
        {activeTab === 'batches' && (
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-6">Imported Batches</h2>
            
            {batches.length === 0 ? (
              <p className="text-gray-400">No batches imported yet</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-gray-700">
                      <th className="pb-3 font-medium">Batch Number</th>
                      <th className="pb-3 font-medium">Product</th>
                      <th className="pb-3 font-medium">Purity</th>
                      <th className="pb-3 font-medium">Expiry Date</th>
                      <th className="pb-3 font-medium">Total</th>
                      <th className="pb-3 font-medium">Verified</th>
                      <th className="pb-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {batches.map((batch, i) => (
                      <tr key={i} className="border-b border-gray-700/50">
                        <td className="py-4 text-white font-mono text-sm">{batch._id}</td>
                        <td className="py-4 text-gray-300 text-sm">{batch.product_name}</td>
                        <td className="py-4 text-gray-300 text-sm">{batch.purity || '-'}</td>
                        <td className="py-4 text-gray-300 text-sm">{batch.expiry_date || '-'}</td>
                        <td className="py-4 text-gray-300">{batch.total_codes}</td>
                        <td className="py-4">
                          <span className={`px-2 py-1 rounded text-sm ${
                            batch.verified_codes > 0 ? 'bg-yellow-900/50 text-yellow-400' : 'bg-gray-700 text-gray-400'
                          }`}>
                            {batch.verified_codes}
                          </span>
                        </td>
                        <td className="py-4 space-x-2">
                          <button
                            onClick={() => openEditBatch(batch)}
                            className="text-blue-400 hover:text-blue-300 text-sm"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleResetBatch(batch._id)}
                            className="text-yellow-400 hover:text-yellow-300 text-sm"
                          >
                            Reset
                          </button>
                          <button
                            onClick={() => handleDeleteBatch(batch._id)}
                            className="text-red-400 hover:text-red-300 text-sm"
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
            
            {/* Edit Batch Modal */}
            {editingBatch && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-gray-800 rounded-xl p-6 w-full max-w-md border border-gray-700">
                  <h3 className="text-lg font-bold text-white mb-4">Edit Batch: {editingBatch}</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-gray-400 text-sm mb-2">Purity</label>
                      <input
                        type="text"
                        value={editPurity}
                        onChange={(e) => setEditPurity(e.target.value)}
                        placeholder="e.g. ≥99%"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-gray-400 text-sm mb-2">Expiry Date</label>
                      <input
                        type="date"
                        value={editExpiryDate}
                        onChange={(e) => setEditExpiryDate(e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                  
                  <div className="flex gap-3 mt-6">
                    <button
                      onClick={() => setEditingBatch(null)}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 rounded-lg"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={saveEditBatch}
                      disabled={savingBatch}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg disabled:opacity-50"
                    >
                      {savingBatch ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Leads Tab */}
        {activeTab === 'leads' && (
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
              <h2 className="text-xl font-bold text-white" data-testid="leads-title">
                Protocol Leads ({leadsTotal})
              </h2>
              <div className="flex items-center gap-3 flex-wrap">
                <input
                  type="text"
                  value={leadsSearch}
                  onChange={(e) => setLeadsSearch(e.target.value)}
                  placeholder="Search name, email, phone..."
                  data-testid="leads-search-input"
                  className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-blue-500 w-64"
                />
                <select
                  value={leadsFilter}
                  onChange={(e) => setLeadsFilter(e.target.value)}
                  data-testid="leads-filter-select"
                  className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Protocols</option>
                  <option value="proto-ghkcu50">GHK-Cu 50mg</option>
                  <option value="proto-ghkcu100">GHK-Cu 100mg</option>
                  <option value="proto-tb500">TB-500</option>
                  <option value="proto-glow-blend">Glow Blend</option>
                  <option value="proto-igf1">IGF-1 LR3</option>
                  <option value="proto-klow-blend">Klow Blend</option>
                  <option value="proto-oxytocin">Oxytocin</option>
                  <option value="proto-retatrutide">Retatrutide</option>
                </select>
                <button
                  onClick={exportLeadsCSV}
                  data-testid="leads-export-btn"
                  className="bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-lg text-sm transition"
                >
                  Export CSV
                </button>
              </div>
            </div>

            {loadingLeads ? (
              <p className="text-gray-400">Loading leads...</p>
            ) : leads.length === 0 ? (
              <p className="text-gray-400" data-testid="leads-empty">No leads found</p>
            ) : (
              <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
                <table className="w-full" data-testid="leads-table">
                  <thead className="sticky top-0 bg-gray-800">
                    <tr className="text-left text-gray-400 border-b border-gray-700">
                      <th className="pb-3 font-medium">Name</th>
                      <th className="pb-3 font-medium">Email</th>
                      <th className="pb-3 font-medium">Phone</th>
                      <th className="pb-3 font-medium">Protocol</th>
                      <th className="pb-3 font-medium">Lang</th>
                      <th className="pb-3 font-medium">Source</th>
                      <th className="pb-3 font-medium">Downloads</th>
                      <th className="pb-3 font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map((lead, i) => (
                      <tr key={i} className="border-b border-gray-700/50" data-testid={`lead-row-${i}`}>
                        <td className="py-3 text-white text-sm">{lead.name || '-'}</td>
                        <td className="py-3 text-blue-400 text-sm">{lead.email}</td>
                        <td className="py-3 text-gray-300 text-sm">{lead.phone || '-'}</td>
                        <td className="py-3 text-gray-300 text-sm">{lead.protocol_title || '-'}</td>
                        <td className="py-3 text-gray-400 text-sm uppercase">{lead.language || '-'}</td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            lead.source === 'website_protocols_v3'
                              ? 'bg-blue-900/50 text-blue-400'
                              : 'bg-gray-700 text-gray-400'
                          }`}>
                            {lead.source === 'website_protocols_v3' ? 'V3 Code' : lead.source === 'website_protocols' ? 'V2 Batch' : lead.source || '-'}
                          </span>
                        </td>
                        <td className="py-3 text-gray-300 text-sm text-center">{lead.download_count || 0}</td>
                        <td className="py-3 text-gray-400 text-sm">
                          {lead.created_at ? new Date(lead.created_at).toLocaleDateString() : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-6">Verification Logs</h2>
            <p className="text-gray-400 text-sm mb-4">
              💡 Same IP/Location = probably same person. Different locations = suspicious.
            </p>
            
            {logs.length === 0 ? (
              <p className="text-gray-400">No verifications yet</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-gray-700">
                      <th className="pb-3 font-medium">Code</th>
                      <th className="pb-3 font-medium">Product</th>
                      <th className="pb-3 font-medium">#</th>
                      <th className="pb-3 font-medium">Location</th>
                      <th className="pb-3 font-medium">IP</th>
                      <th className="pb-3 font-medium">Device</th>
                      <th className="pb-3 font-medium">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log, i) => (
                      <tr key={i} className="border-b border-gray-700/50">
                        <td className="py-4 text-white font-mono text-sm">{log.code}</td>
                        <td className="py-4 text-gray-300 text-sm">{log.product_name}</td>
                        <td className="py-4">
                          <span className={`px-2 py-1 rounded text-sm ${
                            log.verification_number === 1 
                              ? 'bg-green-900/50 text-green-400'
                              : log.verification_number === 2
                                ? 'bg-yellow-900/50 text-yellow-400'
                                : 'bg-red-900/50 text-red-400'
                          }`}>
                            #{log.verification_number}
                          </span>
                        </td>
                        <td className="py-4 text-gray-300 text-sm">
                          {log.country && log.country !== 'Unknown' ? (
                            <span title={`${log.city}, ${log.country}`}>
                              {log.city}, {log.country_code || log.country}
                            </span>
                          ) : '-'}
                        </td>
                        <td className="py-4 text-gray-400 text-xs font-mono">{log.client_ip || '-'}</td>
                        <td className="py-4 text-gray-400 text-xs" title={log.user_agent}>
                          {log.user_agent ? (log.user_agent.includes('Mobile') ? '📱' : '💻') : '-'}
                        </td>
                        <td className="py-4 text-gray-400 text-sm">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Email Template Tab */}
        {activeTab === 'email' && (
          <EmailTab />
        )}
      </div>
    </div>
  );
}


function LabelsTab({ password, apiUrl, codes, batches, lastImportBatchId }) {
  var [selectedBatch, setSelectedBatch] = React.useState('');
  var [batchCodes, setBatchCodes] = React.useState([]);
  var [loadingCodes, setLoadingCodes] = React.useState(false);
  var [manualCodes, setManualCodes] = React.useState('');
  var [selectMode, setSelectMode] = React.useState('batch');

  var handleBatchSelect = async function(batchId) {
    setSelectedBatch(batchId);
    setBatchCodes([]);
    if (!batchId) return;
    setLoadingCodes(true);
    try {
      var res = await fetch(apiUrl + '/api/admin/codes?batch_number=' + encodeURIComponent(batchId) + '&limit=500', {
        headers: { 'x-admin-password': password }
      });
      var data = await res.json();
      setBatchCodes(data.codes || []);
    } catch (err) {
      console.error('Error loading batch codes:', err);
    }
    setLoadingCodes(false);
  };

  var handleLastImport = async function() {
    if (!lastImportBatchId) return;
    setSelectMode('lastimport');
    setBatchCodes([]);
    setLoadingCodes(true);
    try {
      var res = await fetch(apiUrl + '/api/admin/codes?import_batch_id=' + encodeURIComponent(lastImportBatchId) + '&limit=1000', {
        headers: { 'x-admin-password': password }
      });
      var data = await res.json();
      setBatchCodes(data.codes || []);
    } catch (err) {
      console.error('Error loading last import:', err);
    }
    setLoadingCodes(false);
  };

  var getExportCodes = function() {
    if (selectMode === 'batch' || selectMode === 'lastimport') return batchCodes;
    if (selectMode === 'manual' && manualCodes.trim()) {
      return manualCodes.trim().split('\n').map(function(c) { return { code: c.trim(), product_name: '', batch_number: '' }; }).filter(function(c) { return c.code; });
    }
    return [];
  };

  var handleExportCSV = function() {
    var codesToExport = getExportCodes();
    if (codesToExport.length === 0) return;
    
    var rows = codesToExport.map(function(c) {
      var codeRaw = c.code.replace(/-/g, '');
      return {
        'Code': c.code,
        'Verification URL': 'https://zurixsciences.com/verify?code=' + codeRaw,
        'Product': c.product_name || '',
        'Batch': c.batch_number || ''
      };
    });
    
    var ws = XLSX.utils.json_to_sheet(rows);
    
    // Auto-size columns
    ws['!cols'] = [
      { wch: 30 },  // Code
      { wch: 60 },  // Verification URL
      { wch: 25 },  // Product
      { wch: 25 },  // Batch
    ];
    
    var wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Codes');
    XLSX.writeFile(wb, (selectedBatch || 'zurix_codes') + '.xlsx');
  };

  var handleCopyAll = function() {
    var codesToExport = getExportCodes();
    var text = codesToExport.map(function(c) { return c.code; }).join('\n');
    navigator.clipboard.writeText(text);
  };

  var exportCodes = getExportCodes();

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700" data-testid="labels-tab">
      <h2 className="text-xl font-bold text-white mb-2">Export Codes for Labels</h2>
      <p className="text-gray-400 text-sm mb-6">Export verification codes as CSV to import into Niimbot app or Excel for printing labels</p>

      <div className="flex gap-2 mb-6">
        {[
          { id: 'batch', label: 'By Batch' },
          { id: 'lastimport', label: 'Last Import' },
          { id: 'manual', label: 'Manual Codes' },
        ].map(function(m) {
          return (
            <button key={m.id} onClick={function() { setSelectMode(m.id); if (m.id === 'lastimport') handleLastImport(); }}
              className={'px-4 py-2 rounded-lg text-sm font-medium transition ' + (selectMode === m.id ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:text-white') + (m.id === 'lastimport' && !lastImportBatchId ? ' opacity-40 cursor-not-allowed' : '')}
              disabled={m.id === 'lastimport' && !lastImportBatchId}>
              {m.label}{m.id === 'lastimport' && lastImportBatchId ? ' (' + lastImportBatchId + ')' : ''}
            </button>
          );
        })}
      </div>

      {selectMode === 'lastimport' && (
        <div className="mb-6">
          {loadingCodes ? (
            <p className="text-gray-400 text-sm">Loading last imported codes...</p>
          ) : (
            <p className="text-green-400 text-sm">{batchCodes.length} codes from last import ready to export</p>
          )}
        </div>
      )}

      {selectMode === 'batch' && (
        <div className="mb-6">
          <label className="block text-sm text-gray-300 mb-2">Select Batch</label>
          <select value={selectedBatch} onChange={function(e) { handleBatchSelect(e.target.value); }}
            data-testid="label-batch-select"
            className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:border-blue-500">
            <option value="">-- Select a batch --</option>
            {batches.map(function(b) {
              var batchId = b._id || b.batch_number;
              return <option key={batchId} value={batchId}>{b.product_name} — {batchId} ({b.total_codes} codes)</option>;
            })}
          </select>
          {selectedBatch && (
            <p className="text-gray-400 text-sm mt-2">
              {loadingCodes ? 'Loading codes...' : batchCodes.length + ' codes loaded'}
            </p>
          )}
        </div>
      )}

      {selectMode === 'manual' && (
        <div className="mb-6">
          <label className="block text-sm text-gray-300 mb-2">Enter codes (one per line)</label>
          <textarea value={manualCodes} onChange={function(e) { setManualCodes(e.target.value); }}
            data-testid="label-manual-codes"
            rows={6} placeholder={"ZX-260312-GHK50-1-000001\nZX-260312-GHK50-1-000002"}
            className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:border-blue-500 font-mono text-sm" />
        </div>
      )}

      {exportCodes.length > 0 && (
        <div>
          <div className="flex items-center gap-3 mb-4">
            <button onClick={handleExportCSV} data-testid="export-csv-btn"
              className="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-3 rounded-lg transition">
              Export Excel ({exportCodes.length} codes)
            </button>
            <button onClick={handleCopyAll} data-testid="copy-codes-btn"
              className="bg-gray-600 hover:bg-gray-500 text-white font-medium px-5 py-3 rounded-lg transition">
              Copy All Codes
            </button>
          </div>

          <div className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700 bg-gray-900/50">
                  <th className="py-2 px-4 text-left text-gray-400 font-medium">#</th>
                  <th className="py-2 px-4 text-left text-gray-400 font-medium">Code</th>
                  <th className="py-2 px-4 text-left text-gray-400 font-medium">Product</th>
                  <th className="py-2 px-4 text-left text-gray-400 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {exportCodes.slice(0, 20).map(function(c, i) {
                  return (
                    <tr key={c.code} className="border-b border-gray-800">
                      <td className="py-2 px-4 text-gray-500">{i + 1}</td>
                      <td className="py-2 px-4 text-white font-mono text-xs">{c.code}</td>
                      <td className="py-2 px-4 text-gray-300">{c.product_name || '-'}</td>
                      <td className="py-2 px-4">
                        {c.verified_at ? (
                          <span className="text-yellow-400 text-xs">Used</span>
                        ) : (
                          <span className="text-green-400 text-xs">Available</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {exportCodes.length > 20 && (
              <p className="text-gray-500 text-xs text-center py-2">... and {exportCodes.length - 20} more codes</p>
            )}
          </div>

          <div className="mt-4 p-4 bg-blue-900/20 border border-blue-800/30 rounded-lg">
            <p className="text-blue-300 text-sm font-medium mb-1">How to print labels:</p>
            <ol className="text-blue-200/70 text-xs space-y-1 list-decimal list-inside">
              <li>Click "Export Excel" to download the .xlsx file</li>
              <li>Open in Excel or import into Niimbot app</li>
              <li>Use the "Verification URL" column as the QR code data</li>
              <li>Customer scans QR with native camera → auto-verifies on the website</li>
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}


function generateEmailHTML(clientName, responseText) {
  var lines = responseText.split('\n').map(function(line) {
    return '<p style="margin:0 0 12px;font-size:15px;color:#374151;line-height:1.7;">' + line + '</p>';
  }).join('');

  return '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 16px;"><tr><td align="center"><table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);"><tr><td style="padding:32px 40px;text-align:center;border-bottom:3px solid #1e40af;"><h1 style="margin:0;font-size:28px;font-weight:800;color:#1e40af;letter-spacing:-0.5px;">Zurix Sciences</h1><p style="margin:4px 0 0;font-size:12px;color:#6b7280;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">Premium Research Compounds</p></td></tr><tr><td style="padding:40px;"><p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">Dear <span style="color:#1e40af;font-weight:600;">' + clientName + '</span>,</p><p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">Thank you for reaching out to Zurix Sciences. We appreciate your interest in our research-grade peptide products.</p><div style="background-color:#f8fafc;border-left:4px solid #2563eb;border-radius:0 8px 8px 0;padding:20px 24px;margin:24px 0;">' + lines + '</div><p style="margin:24px 0 20px;font-size:15px;color:#374151;line-height:1.7;">Should you have any further questions, please do not hesitate to contact us. We are available Monday through Friday, 9:00 - 18:00 (CET).</p><p style="margin:0 0 8px;font-size:15px;color:#374151;line-height:1.7;">Kind regards,</p><p style="margin:0 0 8px;font-size:15px;color:#374151;line-height:1.7;font-weight:600;">Noah</p></td></tr><tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #e5e7eb;margin:0;"/></td></tr><tr><td style="padding:28px 40px;"><p style="margin:0 0 2px;font-size:16px;font-weight:700;color:#1e3a5f;">Zurix Sciences</p><p style="margin:0 0 12px;font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">Client Relations</p><p style="margin:0 0 4px;font-size:13px;color:#374151;">&#9993; RxpeptidesHK@proton.me</p><p style="margin:0 0 4px;font-size:13px;color:#374151;">&#9830; Threema ID: <strong>2D9DAD9R</strong></p><p style="margin:0 0 4px;font-size:13px;color:#374151;">&#9906; Aeschenvorstadt 71, 4051 Basel, Switzerland</p><p style="margin:0;font-size:13px;"><a href="https://zurixsciences.com" style="color:#2563eb;text-decoration:none;font-weight:600;">zurixsciences.com</a></p></td></tr><tr><td style="background-color:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e5e7eb;"><p style="margin:0 0 4px;font-size:11px;color:#9ca3af;">This email and any attachments are confidential and intended solely for the addressee.</p><p style="margin:0;font-size:11px;color:#9ca3af;">All products are sold strictly for research purposes only. Not for human consumption.</p></td></tr></table></td></tr></table></body></html>';
}

function EmailTab() {
  const [clientName, setClientName] = React.useState('');
  const [responseText, setResponseText] = React.useState('');
  const [copied, setCopied] = React.useState(false);
  const [showPreview, setShowPreview] = React.useState(false);
  const iframeRef = React.useRef(null);

  function handleGenerate() {
    if (!clientName.trim() || !responseText.trim()) return;
    setShowPreview(true);
    setTimeout(function() {
      if (iframeRef.current) {
        var doc = iframeRef.current.contentDocument;
        doc.open();
        doc.write(generateEmailHTML(clientName, responseText));
        doc.close();
      }
    }, 100);
  }

  function handleCopy() {
    var html = generateEmailHTML(clientName, responseText);
    var blob = new Blob([html], { type: 'text/html' });
    var plainText = 'Dear ' + clientName + ',\n\nThank you for reaching out to Zurix Sciences.\n\n' + responseText + '\n\nKind regards,\nZurix Sciences\nClient Relations\nRxpeptidesHK@proton.me\nThreema ID: 2D9DAD9R\nAeschenvorstadt 71, 4051 Basel, Switzerland\nzurixsciences.com';
    var textBlob = new Blob([plainText], { type: 'text/plain' });
    var item = new ClipboardItem({
      'text/html': blob,
      'text/plain': textBlob,
    });
    navigator.clipboard.write([item]).then(function() {
      setCopied(true);
      setTimeout(function() { setCopied(false); }, 2000);
    }).catch(function() {
      navigator.clipboard.writeText(plainText).then(function() {
        setCopied(true);
        setTimeout(function() { setCopied(false); }, 2000);
      });
    });
  }

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-6">Email Template Generator</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-gray-400 text-sm mb-2">Client Name</label>
            <input
              type="text"
              value={clientName}
              onChange={function(e) { setClientName(e.target.value); }}
              placeholder="John Smith"
              className="w-full px-4 py-2.5 bg-gray-900 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-gray-400 text-sm mb-2">Your Response</label>
            <textarea
              value={responseText}
              onChange={function(e) { setResponseText(e.target.value); }}
              placeholder="Type your response to the client here..."
              rows={10}
              className="w-full px-4 py-2.5 bg-gray-900 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleGenerate}
              disabled={!clientName.trim() || !responseText.trim()}
              className="flex-1 bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-40"
            >
              Generate Preview
            </button>
            {showPreview && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-2 bg-green-600 text-white font-semibold px-5 py-2.5 rounded-lg hover:bg-green-700 transition-colors"
              >
                {copied ? '✓ Copied!' : '📋 Copy Email'}
              </button>
            )}
          </div>
          {showPreview && (
            <div className="bg-blue-900/20 border border-blue-800/30 rounded-lg p-3">
              <p className="text-blue-300 text-xs leading-relaxed">
                <strong>ProtonMail:</strong> Click "Copy Email", then paste directly in the ProtonMail composer (Ctrl+V). The formatting will be preserved.
              </p>
            </div>
          )}
        </div>
        <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden">
          <div className="bg-gray-700 px-4 py-2 border-b border-gray-600">
            <span className="text-sm font-medium text-gray-300">Email Preview</span>
          </div>
          {showPreview ? (
            <iframe
              ref={iframeRef}
              title="Email Preview"
              className="w-full border-0 bg-white"
              style={{ height: '500px' }}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 text-sm">
              Fill in the form and click "Generate Preview"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

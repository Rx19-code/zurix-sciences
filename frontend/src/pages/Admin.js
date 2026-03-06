import React, { useState, useEffect } from 'react';

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
  const [codesText, setCodesText] = useState('');
  const [importResult, setImportResult] = useState(null);
  
  // Data views
  const [products, setProducts] = useState([]);
  const [batches, setBatches] = useState([]);
  const [codes, setCodes] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('import');
  const [searchCode, setSearchCode] = useState('');
  const [searching, setSearching] = useState(false);
  const [codesTotal, setCodesTotal] = useState(0);
  const [hasMoreCodes, setHasMoreCodes] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  
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
          codes: codes
        })
      });
      
      const data = await res.json();
      setImportResult(data);
      
      if (data.success) {
        setCodesText('');
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
  
  // Use codes directly since search is server-side now
  const filteredCodes = codes;
  
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
            { id: 'codes', label: 'All Codes', icon: '🔑' },
            { id: 'batches', label: 'Batches', icon: '📦' },
            { id: 'logs', label: 'Verification Logs', icon: '📋' },
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
        
        {/* Codes Tab */}
        {activeTab === 'codes' && (
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">
                All Codes ({codes.length} of {codesTotal})
                {searching && <span className="ml-2 text-blue-400 text-sm">Searching...</span>}
              </h2>
              <input
                type="text"
                value={searchCode}
                onChange={(e) => setSearchCode(e.target.value)}
                placeholder="Search code, product or batch (min 2 chars)..."
                className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-blue-500 w-72"
              />
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
                          {code.verification_count >= 3 ? (
                            <span className="text-red-400 text-sm">Blocked</span>
                          ) : code.verification_count > 0 ? (
                            <span className="text-yellow-400 text-sm">Used</span>
                          ) : (
                            <span className="text-green-400 text-sm">New</span>
                          )}
                        </td>
                        <td className="py-3">
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
                      <th className="pb-3 font-medium">Total Codes</th>
                      <th className="pb-3 font-medium">Verified</th>
                      <th className="pb-3 font-medium">Created</th>
                      <th className="pb-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {batches.map((batch, i) => (
                      <tr key={i} className="border-b border-gray-700/50">
                        <td className="py-4 text-white font-mono">{batch._id}</td>
                        <td className="py-4 text-gray-300">{batch.product_name}</td>
                        <td className="py-4 text-gray-300">{batch.total_codes}</td>
                        <td className="py-4">
                          <span className={`px-2 py-1 rounded text-sm ${
                            batch.verified_codes > 0 ? 'bg-yellow-900/50 text-yellow-400' : 'bg-gray-700 text-gray-400'
                          }`}>
                            {batch.verified_codes}
                          </span>
                        </td>
                        <td className="py-4 text-gray-400 text-sm">
                          {batch.created_at ? new Date(batch.created_at).toLocaleDateString() : '-'}
                        </td>
                        <td className="py-4">
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
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { FileText, Clock, Download, X, CheckCircle, Globe, Lock, Unlock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Protocols = () => {
  const [protocols, setProtocols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [batchNumber, setBatchNumber] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchProtocols();
  }, []);

  const fetchProtocols = async () => {
    try {
      const response = await fetch(`${API}/protocols-v2`);
      const data = await response.json();
      if (data.success) {
        setProtocols(data.protocols);
      }
    } catch (error) {
      console.error('Error fetching protocols:', error);
    } finally {
      setLoading(false);
    }
  };

  const openProtocol = (protocol) => {
    setSelectedProtocol(protocol);
    setBatchNumber('');
    setValidationResult(null);
  };

  const closeModal = () => {
    setSelectedProtocol(null);
    setBatchNumber('');
    setValidationResult(null);
  };

  const validateBatch = async () => {
    if (!batchNumber.trim()) return;
    
    setValidating(true);
    setValidationResult(null);
    
    try {
      const response = await fetch(`${API}/protocols-v2/validate-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protocol_id: selectedProtocol.id,
          batch_number: batchNumber.trim()
        })
      });
      const data = await response.json();
      setValidationResult(data);
    } catch (error) {
      console.error('Error validating batch:', error);
      setValidationResult({
        success: false,
        valid: false,
        message: 'Error validating batch. Please try again.'
      });
    } finally {
      setValidating(false);
    }
  };

  const downloadProtocol = async (language) => {
    setDownloading(true);
    try {
      const downloadUrl = `${API}/protocols-v2/download?protocol_id=${selectedProtocol.id}&batch_number=${encodeURIComponent(batchNumber.trim())}&language=${language}`;
      window.open(downloadUrl, '_blank');
    } catch (error) {
      console.error('Error downloading protocol:', error);
    } finally {
      setDownloading(false);
    }
  };

  const getCategoryColor = (category) => {
    switch (category?.toLowerCase()) {
      case 'basic':
        return 'bg-blue-100 text-blue-800';
      case 'advanced':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="protocols-page">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white bg-opacity-10 backdrop-blur-lg rounded-full mb-6">
            <FileText className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4" data-testid="protocols-title">
            Research Protocols
          </h1>
          <p className="text-lg text-blue-100 max-w-2xl mx-auto">
            Access detailed research protocols for Zurix Sciences peptides. Free download with a valid product batch number.
          </p>
        </div>
      </div>

      {/* How It Works */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 mb-12">
          <h2 className="text-lg font-bold text-blue-900 mb-4 flex items-center gap-2">
            <Lock className="w-5 h-5" />
            How to Access Protocols
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">1</span>
              <div>
                <p className="font-medium text-blue-900">Purchase Product</p>
                <p className="text-sm text-blue-700">Buy any Zurix Sciences peptide</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">2</span>
              <div>
                <p className="font-medium text-blue-900">Find Batch Number</p>
                <p className="text-sm text-blue-700">Located on product label (ZX-XXXXXX...)</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">3</span>
              <div>
                <p className="font-medium text-blue-900">Download Protocol</p>
                <p className="text-sm text-blue-700">Enter batch to unlock free PDF</p>
              </div>
            </div>
          </div>
        </div>

        {/* Protocols Grid */}
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Protocols</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {protocols.map((protocol) => (
            <div
              key={protocol.id}
              className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100 overflow-hidden cursor-pointer"
              onClick={() => openProtocol(protocol)}
              data-testid={`protocol-card-${protocol.id}`}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getCategoryColor(protocol.category)}`}>
                    {protocol.category}
                  </span>
                  <span className="text-green-600 font-bold text-sm flex items-center gap-1">
                    <Unlock className="w-4 h-4" />
                    FREE
                  </span>
                </div>
                
                <h3 className="text-lg font-bold text-gray-900 mb-2">{protocol.title}</h3>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{protocol.description}</p>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{protocol.duration_weeks} weeks</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Globe className="w-4 h-4" />
                    <span>EN | ES | PT</span>
                  </div>
                </div>
              </div>
              
              <div className="px-6 py-3 bg-gray-50 border-t border-gray-100">
                <button className="w-full text-blue-600 font-semibold text-sm hover:text-blue-700 flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Access Protocol
                </button>
              </div>
            </div>
          ))}
        </div>

        {protocols.length === 0 && (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No protocols available at the moment.</p>
          </div>
        )}
      </div>

      {/* Protocol Modal */}
      {selectedProtocol && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto" data-testid="protocol-modal">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-900">{selectedProtocol.title}</h3>
              <button
                onClick={closeModal}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                data-testid="close-modal-button"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <p className="text-gray-600 mb-4">{selectedProtocol.description}</p>
              
              <div className="flex items-center gap-4 mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Clock className="w-4 h-4" />
                  <span>{selectedProtocol.duration_weeks} weeks</span>
                </div>
                <span className="text-green-600 font-semibold text-sm">FREE with valid batch</span>
              </div>

              {/* Batch Validation */}
              <div className="bg-gray-50 rounded-xl p-4 mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter Product Batch Number
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={batchNumber}
                    onChange={(e) => setBatchNumber(e.target.value.toUpperCase())}
                    placeholder="ZX-XXXXXX-XXXX-X"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    data-testid="batch-number-input"
                  />
                  <button
                    onClick={validateBatch}
                    disabled={validating || !batchNumber.trim()}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold rounded-lg transition-colors whitespace-nowrap"
                    data-testid="validate-batch-button"
                  >
                    {validating ? 'Checking...' : 'Validate'}
                  </button>
                </div>
                <p className="mt-2 text-xs text-gray-500">
                  Find the batch number on your product label
                </p>
              </div>

              {/* Validation Result */}
              {validationResult && (
                <div className={`rounded-xl p-4 mb-4 ${validationResult.valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`} data-testid="validation-result">
                  <div className="flex items-start gap-3">
                    {validationResult.valid ? (
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    ) : (
                      <X className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className={`font-medium ${validationResult.valid ? 'text-green-800' : 'text-red-800'}`}>
                        {validationResult.valid ? 'Batch Validated!' : 'Validation Failed'}
                      </p>
                      <p className={`text-sm ${validationResult.valid ? 'text-green-700' : 'text-red-700'}`}>
                        {validationResult.message}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Download Options */}
              {validationResult?.valid && (
                <div className="space-y-3" data-testid="download-options">
                  <p className="font-medium text-gray-900">Select Language:</p>
                  <div className="grid grid-cols-3 gap-3">
                    {validationResult.available_languages?.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => downloadProtocol(lang.code)}
                        disabled={downloading}
                        className="flex flex-col items-center gap-2 p-4 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl transition-colors"
                        data-testid={`download-${lang.code}`}
                      >
                        <Download className="w-6 h-6 text-blue-600" />
                        <span className="text-sm font-semibold text-blue-900">{lang.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Protocols;

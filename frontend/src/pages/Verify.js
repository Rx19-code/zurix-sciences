import React, { useState } from 'react';
import { Shield, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Verify = () => {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const sampleCodes = ['CS-ZE101208', 'CS-BP050823', 'CS-SE030409', 'CS-FAKE-0001'];

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API}/verify-product`, { code: code.trim().toUpperCase() });
      setResult(response.data);
    } catch (error) {
      console.error('Error verifying product:', error);
      setResult({
        success: false,
        message: 'Error verifying product. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTestCode = (testCode) => {
    setCode(testCode);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900" data-testid="verify-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white bg-opacity-10 backdrop-blur-lg rounded-full mb-6">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4" data-testid="verify-title">
            Product Authentication System
          </h1>
          <p className="text-xl text-blue-100">
            Verify the authenticity of your Zurix Science products using the unique verification code on your vial or packaging.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Verification Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Verify Product</h2>
            <p className="text-gray-600 mb-6">
              Enter your unique product code to verify authenticity
            </p>

            <form onSubmit={handleVerify} className="space-y-6">
              <div>
                <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
                  Product Verification Code
                </label>
                <input
                  type="text"
                  id="code"
                  value={code}
                  onChange={(e) => setCode(e.target.value.toUpperCase())}
                  data-testid="verification-code-input"
                  placeholder="Enter code (e.g., CS-ZE101208)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-lg"
                  required
                />
                <p className="mt-2 text-sm text-gray-500">
                  Example: CS-ze101208, CS-re10-1220, CS-bc101103
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                data-testid="verify-button"
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5" />
                    <span>Verify</span>
                  </>
                )}
              </button>
            </form>

            {/* Test Codes */}
            <div className="mt-8 bg-blue-50 rounded-lg p-4">
              <div className="flex items-start space-x-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-blue-900 text-sm">Test with sample codes:</h3>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {sampleCodes.map((sampleCode) => (
                  <button
                    key={sampleCode}
                    onClick={() => handleTestCode(sampleCode)}
                    data-testid={`test-code-${sampleCode}`}
                    className="px-3 py-1 bg-white border border-blue-200 hover:border-blue-400 text-blue-600 text-sm font-mono rounded transition-colors"
                  >
                    {sampleCode}
                  </button>
                ))}
              </div>
            </div>

            {/* Result */}
            {result && (
              <div className="mt-6" data-testid="verification-result">
                {result.success ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <div className="flex items-start space-x-3 mb-4">
                      <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                      <div>
                        <h3 className="font-bold text-green-900 text-lg">Product Authenticated!</h3>
                        <p className="text-green-700 text-sm">{result.message}</p>
                      </div>
                    </div>

                    {result.product && (
                      <div className="space-y-3 pt-4 border-t border-green-200">
                        <h4 className="font-semibold text-green-900">Product Details:</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-green-700">Product:</span>
                            <span className="font-semibold text-green-900" data-testid="verified-product-name">
                              {result.product.name}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-green-700">Batch:</span>
                            <span className="font-mono font-semibold text-green-900">
                              {result.product.batch_number}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-green-700">Manufacturing Date:</span>
                            <span className="font-semibold text-green-900">
                              {result.product.manufacturing_date}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-green-700">Expiry Date:</span>
                            <span className="font-semibold text-green-900">
                              {result.product.expiry_date}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-green-700">Purity:</span>
                            <span className="font-semibold text-green-900">
                              {result.product.purity}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <div className="flex items-start space-x-3">
                      <XCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
                      <div>
                        <h3 className="font-bold text-red-900 text-lg">Verification Failed</h3>
                        <p className="text-red-700 text-sm mt-1" data-testid="verification-error-message">{result.message}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Why Verify Panel */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Shield className="w-6 h-6 text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Why Verify?</h2>
              </div>

              <div className="space-y-4">
                {[
                  { icon: CheckCircle, text: 'Confirm product authenticity and origin' },
                  { icon: CheckCircle, text: 'Verify batch information and manufacturing date' },
                  { icon: CheckCircle, text: 'Access Certificate of Analysis (COA)' },
                  { icon: CheckCircle, text: 'Check expiration date and storage recommendations' },
                  { icon: CheckCircle, text: 'Report counterfeit products for investigation' }
                ].map((item, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <item.icon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <p className="text-gray-700">{item.text}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6">
              <div className="flex items-start space-x-3">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-bold text-lg">!</span>
                </div>
                <div>
                  <h3 className="font-bold text-blue-900 mb-2">Important</h3>
                  <p className="text-sm text-blue-800">
                    Every genuine Zurix Science product has a unique verification code starting with "ZX-". 
                    If your product doesn't have one or verification fails, please contact our support team immediately.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Verify;
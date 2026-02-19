import React, { useState } from 'react';
import { Shield, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Verify = () => {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API}/verify-product`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code.trim().toUpperCase() })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error verifying product:', error);
      setResult({
        success: false,
        message: 'Error verifying product. Please try again.',
        warning_level: 'danger'
      });
    } finally {
      setLoading(false);
    }
  };

  const getResultStyles = () => {
    if (!result) return {};
    
    if (!result.success) {
      return {
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: XCircle,
        iconColor: 'text-red-600',
        titleColor: 'text-red-900',
        textColor: 'text-red-700'
      };
    }
    
    switch (result.warning_level) {
      case 'danger':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: AlertTriangle,
          iconColor: 'text-red-600',
          titleColor: 'text-red-900',
          textColor: 'text-red-700'
        };
      case 'caution':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: AlertTriangle,
          iconColor: 'text-yellow-600',
          titleColor: 'text-yellow-900',
          textColor: 'text-yellow-700'
        };
      default:
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: CheckCircle,
          iconColor: 'text-green-600',
          titleColor: 'text-green-900',
          textColor: 'text-green-700'
        };
    }
  };

  const styles = getResultStyles();

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
            Verify the authenticity of your Zurix Sciences products using the unique QR code or verification code.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Verification Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Verify Product</h2>
            <p className="text-gray-600 mb-6">
              Enter the unique code from your product label or scan the QR code
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
                  placeholder="Enter code (e.g., ZX-261216-RT10-1-00038A)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-lg"
                  required
                />
                <p className="mt-2 text-sm text-gray-500">
                  Format: ZX-XXXXXX-XXXX-X-XXXXXX
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
                    <span>Verify Product</span>
                  </>
                )}
              </button>
            </form>

            {/* Result */}
            {result && (
              <div className="mt-6" data-testid="verification-result">
                <div className={`${styles.bg} border ${styles.border} rounded-lg p-6`}>
                  <div className="flex items-start space-x-3 mb-4">
                    <styles.icon className={`w-6 h-6 ${styles.iconColor} flex-shrink-0`} />
                    <div>
                      <h3 className={`font-bold ${styles.titleColor} text-lg`}>
                        {result.success 
                          ? result.warning_level === 'none' 
                            ? '✅ Product Authenticated!' 
                            : result.warning_level === 'caution'
                              ? '⚠️ Verification Warning'
                              : '🚨 High Risk Alert'
                          : '❌ Verification Failed'
                        }
                      </h3>
                      <p className={`${styles.textColor} text-sm mt-1`}>{result.message}</p>
                    </div>
                  </div>

                  {/* Verification count warning */}
                  {result.verification_count > 1 && (
                    <div className={`mt-4 p-3 rounded-lg ${
                      result.verification_count >= 3 ? 'bg-red-100' : 'bg-yellow-100'
                    }`}>
                      <p className={`text-sm font-medium ${
                        result.verification_count >= 3 ? 'text-red-800' : 'text-yellow-800'
                      }`}>
                        ⚠️ This code has been verified {result.verification_count} times.
                        {result.first_verified_at && (
                          <span className="block mt-1">
                            First verification: {new Date(result.first_verified_at).toLocaleString()}
                          </span>
                        )}
                      </p>
                    </div>
                  )}

                  {result.product && (
                    <div className="space-y-3 pt-4 border-t border-gray-200 mt-4">
                      <h4 className={`font-semibold ${styles.titleColor}`}>Product Details:</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className={styles.textColor}>Product:</span>
                          <span className={`font-semibold ${styles.titleColor}`} data-testid="verified-product-name">
                            {result.product.name}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className={styles.textColor}>Batch:</span>
                          <span className={`font-mono font-semibold ${styles.titleColor}`}>
                            {result.product.batch_number}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className={styles.textColor}>Purity:</span>
                          <span className={`font-semibold ${styles.titleColor}`}>
                            {result.product.purity}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className={styles.textColor}>Expiry Date:</span>
                          <span className={`font-semibold ${styles.titleColor}`}>
                            {result.product.expiry_date}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
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
                  { icon: CheckCircle, text: 'Each product has a unique verification code' },
                  { icon: CheckCircle, text: 'First-time verification confirms genuine product' },
                  { icon: CheckCircle, text: 'Multiple verifications may indicate counterfeiting' },
                  { icon: CheckCircle, text: 'Report suspicious products immediately' }
                ].map((item, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <item.icon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <p className="text-gray-700">{item.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Verification Guide */}
            <div className="bg-gray-900 rounded-2xl p-6 text-white">
              <h3 className="font-bold text-lg mb-4">Verification Results Guide</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="w-3 h-3 rounded-full bg-green-500"></span>
                  <span className="text-sm"><strong>1st verification:</strong> Product is authentic</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                  <span className="text-sm"><strong>2nd verification:</strong> Caution - may be counterfeit</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-3 h-3 rounded-full bg-red-500"></span>
                  <span className="text-sm"><strong>3+ verifications:</strong> High risk of counterfeit</span>
                </div>
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
                    Every genuine Zurix Sciences product has a unique verification code starting with "ZX-". 
                    If verification fails or shows multiple verifications, please contact support immediately.
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
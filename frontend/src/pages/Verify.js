import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Shield, CheckCircle, XCircle, AlertTriangle, Camera, Keyboard, X } from 'lucide-react';
import { Html5Qrcode } from 'html5-qrcode';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Verify = () => {
  const [searchParams] = useSearchParams();
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [autoVerified, setAutoVerified] = useState(false);
  const scannerRef = useRef(null);

  // Auto-verify if ?code= is in URL (from native camera QR scan)
  useEffect(function() {
    var urlCode = searchParams.get('code');
    if (urlCode && !autoVerified) {
      setAutoVerified(true);
      var cleanCode = urlCode.trim().toUpperCase();
      setCode(cleanCode);
      verifyCode(cleanCode);
    }
  }, [searchParams]);

  var verifyCode = async function(codeToVerify) {
    if (!codeToVerify || !codeToVerify.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      var response = await fetch(API + '/verify-product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: codeToVerify.trim().toUpperCase() })
      });
      var data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        success: false,
        message: 'Connection error. Please check your internet and try again.',
        warning_level: 'danger'
      });
    } finally {
      setLoading(false);
    }
  };

  // Start QR Scanner
  const startScanner = async () => {
    setCameraError(null);
    setShowScanner(true);
    
    // Wait for DOM element to be ready
    await new Promise(resolve => setTimeout(resolve, 200));
    
    try {
      const html5QrCode = new Html5Qrcode("qr-reader");
      scannerRef.current = html5QrCode;
      
      // Simple, reliable config - let the device handle resolution/focus
      await html5QrCode.start(
        { facingMode: "environment" },
        { 
          fps: 10,
          qrbox: function(viewfinderWidth, viewfinderHeight) {
            // Use 70% of the smaller dimension for scan area
            var minDim = Math.min(viewfinderWidth, viewfinderHeight);
            var size = Math.floor(minDim * 0.7);
            return { width: size, height: size };
          },
          aspectRatio: 1.0,
          experimentalFeatures: {
            useBarCodeDetectorIfSupported: true
          }
        },
        (decodedText) => {
          handleQRCodeDetected(decodedText);
        },
        (errorMessage) => {
          // Ignore scan errors
        }
      );

      // After scanner starts, try to apply focus constraints to the active stream
      try {
        var videoElem = document.querySelector('#qr-reader video');
        if (videoElem && videoElem.srcObject) {
          var track = videoElem.srcObject.getVideoTracks()[0];
          var capabilities = track.getCapabilities ? track.getCapabilities() : {};
          var constraints = {};
          if (capabilities.focusMode && capabilities.focusMode.includes('continuous')) {
            constraints.focusMode = 'continuous';
          }
          if (capabilities.focusDistance) {
            // Set focus for close range (10-20cm)
            constraints.focusDistance = capabilities.focusDistance.min + 
              (capabilities.focusDistance.max - capabilities.focusDistance.min) * 0.15;
          }
          if (Object.keys(constraints).length > 0) {
            await track.applyConstraints({ advanced: [constraints] });
          }
        }
      } catch (focusErr) {
        // Focus adjustment is optional, ignore errors
      }
    } catch (err) {
      console.error('Camera error:', err);
      let errorMsg = 'Could not access camera. ';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMsg += 'Please allow camera access in your browser settings.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMsg += 'No camera found on this device.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMsg += 'Camera is being used by another application.';
      } else {
        errorMsg += 'Please enter the code manually.';
      }
      setCameraError(errorMsg);
      setShowScanner(false);
    }
  };

  const stopScanner = async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop();
        scannerRef.current = null;
      } catch (err) {
        console.error('Error stopping scanner:', err);
      }
    }
    setShowScanner(false);
  };

  const handleQRCodeDetected = async (qrCode) => {
    let extractedCode = qrCode;
    
    if (qrCode.includes('verify') || qrCode.includes('code=')) {
      const urlParams = new URLSearchParams(qrCode.split('?')[1]);
      extractedCode = urlParams.get('code') || qrCode;
    }
    
    if (qrCode.match(/ZX-[\w-]+/i)) {
      const match = qrCode.match(/ZX-[\w-]+/i);
      extractedCode = match[0];
    }
    
    const cleanCode = extractedCode.trim().toUpperCase();
    setCode(cleanCode);
    await stopScanner();
    await verifyCode(cleanCode);
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    await verifyCode(code);
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
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4" data-testid="verify-title">
            Product Authentication
          </h1>
          <p className="text-lg text-blue-100">
            Verify the authenticity of your Zurix Sciences products
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Verification Form */}
          <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">Verify Product</h2>
            
            {/* Simple instruction */}
            <div className="mb-6">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <p className="text-sm text-blue-800 font-medium mb-1">How to verify:</p>
                <p className="text-xs text-blue-600">Scan the QR code on your product with your phone's camera — it will open this page and verify automatically. Or enter the code manually below.</p>
              </div>
              {/* Camera error removed - using native camera only */}
            </div>

            <form id="verify-form" onSubmit={handleVerify} className="space-y-6">
              <div>
                <label htmlFor="code-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Product Verification Code
                </label>
                <input
                  type="text"
                  id="code-input"
                  value={code}
                  onChange={(e) => setCode(e.target.value.toUpperCase())}
                  data-testid="verification-code-input"
                  placeholder="ZX-XXXXXX-XXXX-X-XXXXXX"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-base sm:text-lg"
                  required
                />
                <p className="mt-2 text-xs sm:text-sm text-gray-500">
                  Find the code on your product label
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || !code.trim()}
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
                <div className={`${styles.bg} border ${styles.border} rounded-lg p-4 sm:p-6`}>
                  <div className="flex items-start space-x-3 mb-4">
                    <styles.icon className={`w-6 h-6 ${styles.iconColor} flex-shrink-0`} />
                    <div>
                      <h3 className={`font-bold ${styles.titleColor} text-base sm:text-lg`}>
                        {result.success 
                          ? result.warning_level === 'none' 
                            ? 'Product Authenticated!' 
                            : result.warning_level === 'caution'
                              ? 'Verification Warning'
                              : 'High Risk Alert'
                          : 'Verification Failed'
                        }
                      </h3>
                      <p className={`${styles.textColor} text-sm mt-1`}>{result.message}</p>
                    </div>
                  </div>

                  {/* Verification count warning */}
                  {result.verification_count >= 3 && (
                    <div className={`mt-4 p-3 rounded-lg ${
                      result.verification_count >= 4 ? 'bg-red-100' : 'bg-yellow-100'
                    }`}>
                      <p className={`text-sm font-medium ${
                        result.verification_count >= 4 ? 'text-red-800' : 'text-yellow-800'
                      }`}>
                        This code has been verified {result.verification_count} times.
                        {result.first_verified_at && (
                          <span className="block mt-1 text-xs">
                            First verification: {new Date(result.first_verified_at).toLocaleString()}
                          </span>
                        )}
                      </p>
                    </div>
                  )}

                  {(result.product_name || result.product) && (
                    <div className="space-y-3 pt-4 border-t border-gray-200 mt-4">
                      <h4 className={`font-semibold ${styles.titleColor} text-sm`}>Product Details:</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className={styles.textColor}>Product:</span>
                          <span className={`font-semibold ${styles.titleColor}`} data-testid="verified-product-name">
                            {result.product_name || (result.product && result.product.name) || '-'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className={styles.textColor}>Batch:</span>
                          <span className={`font-mono font-semibold ${styles.titleColor} text-xs`}>
                            {result.batch_number || (result.product && result.product.batch_number) || '-'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className={styles.textColor}>Purity:</span>
                          <span className={`font-semibold ${styles.titleColor}`}>
                            {result.purity || (result.product && result.product.purity) || '-'}
                          </span>
                        </div>
                        {(result.expiry_date || (result.product && result.product.expiry_date)) && (
                          <div className="flex justify-between">
                            <span className={styles.textColor}>Expiry Date:</span>
                            <span className={`font-semibold ${styles.titleColor}`}>
                              {result.expiry_date || result.product.expiry_date}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Why Verify Panel */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Shield className="w-6 h-6 text-blue-600" />
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Why Verify?</h2>
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
                    <p className="text-gray-700 text-sm sm:text-base">{item.text}</p>
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
                  <span className="text-sm"><strong>1st - 2nd verification:</strong> Product is authentic</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                  <span className="text-sm"><strong>3rd verification:</strong> Attention - product verified multiple times</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-3 h-3 rounded-full bg-red-500"></span>
                  <span className="text-sm"><strong>4+ verifications:</strong> High risk of counterfeit</span>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 sm:p-6">
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

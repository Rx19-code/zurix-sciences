import React, { useState, useEffect } from 'react';
import { FileText, Clock, X, CheckCircle, Globe, Lock, Unlock, Mail, Phone, User, Send, Loader2, CreditCard, Copy, ExternalLink, Shield, ArrowRight, RotateCcw } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Protocols = () => {
  // Code validation state
  const [verificationCode, setVerificationCode] = useState('');
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  // Contact form state
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  const [sending, setSending] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [emailError, setEmailError] = useState(null);

  // Paid protocols state
  const [protocols, setProtocols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPaidProtocol, setSelectedPaidProtocol] = useState(null);
  const [paymentOrder, setPaymentOrder] = useState(null);
  const [txid, setTxid] = useState('');
  const [verifyingPayment, setVerifyingPayment] = useState(false);
  const [paymentResult, setPaymentResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [paidEmail, setPaidEmail] = useState('');
  const [paidPhone, setPaidPhone] = useState('');
  const [paidName, setPaidName] = useState('');
  const [paidLanguage, setPaidLanguage] = useState(null);
  const [paidSending, setPaidSending] = useState(false);
  const [paidEmailError, setPaidEmailError] = useState(null);
  const [paidEmailSent, setPaidEmailSent] = useState(false);

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

  const validateCode = async () => {
    if (!verificationCode.trim()) return;
    setValidating(true);
    setValidationResult(null);
    setEmailSent(false);
    setEmailError(null);

    try {
      const response = await fetch(`${API}/protocols-v2/validate-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: verificationCode.trim() })
      });
      const data = await response.json();
      setValidationResult(data);
    } catch (error) {
      setValidationResult({
        success: false,
        valid: false,
        message: 'Error validating code. Please try again.'
      });
    } finally {
      setValidating(false);
    }
  };

  const sendProtocol = async () => {
    if (!email.trim() || !selectedLanguage) return;
    setSending(true);
    setEmailError(null);

    try {
      const response = await fetch(`${API}/protocols-v2/send-protocol`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: verificationCode.trim(),
          language: selectedLanguage,
          email: email.trim(),
          phone: phone.trim() || null,
          name: name.trim() || null
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setEmailSent(true);
      } else {
        setEmailError(data.detail || data.message || 'Failed to send protocol. Please try again.');
      }
    } catch (error) {
      setEmailError('Network error. Please check your connection and try again.');
    } finally {
      setSending(false);
    }
  };

  const resetForm = () => {
    setVerificationCode('');
    setValidationResult(null);
    setEmail('');
    setPhone('');
    setName('');
    setSelectedLanguage(null);
    setEmailSent(false);
    setEmailError(null);
  };

  // Paid protocol functions
  const openPaidProtocol = (protocol) => {
    setSelectedPaidProtocol(protocol);
    setPaidEmail('');
    setPaidPhone('');
    setPaidName('');
    setPaidLanguage(null);
    setPaymentOrder(null);
    setTxid('');
    setPaymentResult(null);
    setPaidEmailSent(false);
    setPaidEmailError(null);
  };

  const closePaidModal = () => {
    setSelectedPaidProtocol(null);
    setPaymentOrder(null);
    setTxid('');
    setPaymentResult(null);
    setPaidEmailSent(false);
    setPaidEmailError(null);
  };

  const createPaymentOrder = async () => {
    if (!paidEmail.trim() || !paidLanguage) return;
    setPaidSending(true);
    setPaidEmailError(null);

    try {
      const response = await fetch(`${API}/payment/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protocol_id: selectedPaidProtocol.id,
          language: paidLanguage,
          email: paidEmail.trim(),
          phone: paidPhone.trim() || null,
          name: paidName.trim() || null
        })
      });

      const data = await response.json();
      if (response.ok && data.success) {
        setPaymentOrder(data);
      } else {
        setPaidEmailError(data.detail || 'Failed to create order. Please try again.');
      }
    } catch (error) {
      setPaidEmailError('Network error. Please try again.');
    } finally {
      setPaidSending(false);
    }
  };

  const verifyPayment = async () => {
    if (!txid.trim() || !paymentOrder) return;
    setVerifyingPayment(true);
    setPaymentResult(null);

    try {
      const response = await fetch(`${API}/payment/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: paymentOrder.order_id,
          txid: txid.trim()
        })
      });

      const data = await response.json();
      setPaymentResult(data);
      if (data.success && data.paid) {
        setPaidEmailSent(true);
      }
    } catch (error) {
      setPaymentResult({
        success: false,
        message: 'Error verifying payment. Please try again.'
      });
    } finally {
      setVerifyingPayment(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const freeProtocols = protocols.filter(p => p.price === 0 || p.requires_batch);
  const paidProtocols = protocols.filter(p => p.price > 0 && !p.requires_batch);

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
            Access detailed research protocols for Zurix Sciences peptides
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Free Protocol Access Section */}
        <div className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="w-6 h-6 text-green-600" />
            <h2 className="text-2xl font-bold text-gray-900">Get Your Free Protocol</h2>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <p className="text-blue-800 text-sm">
              <strong>How it works:</strong> Enter the unique verification code from your product's QR label. Each code grants a single, personalized protocol download sent directly to your email.
            </p>
          </div>

          {/* Available Free Protocols Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            {freeProtocols.map((protocol) => (
              <div
                key={protocol.id}
                className="bg-white rounded-xl shadow-sm border border-gray-100 p-5"
                data-testid={`protocol-card-${protocol.id}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                    {protocol.category}
                  </span>
                  <span className="text-green-600 font-bold text-xs flex items-center gap-1">
                    <Unlock className="w-3.5 h-3.5" />
                    FREE
                  </span>
                </div>
                <h3 className="text-base font-bold text-gray-900 mb-1.5">{protocol.title}</h3>
                <p className="text-gray-500 text-xs mb-3 line-clamp-2">{protocol.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{protocol.duration_weeks} weeks</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Globe className="w-3.5 h-3.5" />
                    <span>EN | ES | PT</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Success State */}
          <div className="max-w-2xl mx-auto">
          {emailSent ? (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 text-center" data-testid="email-sent-success">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Protocol Sent!</h3>
              <p className="text-gray-600 mb-2">
                Your watermarked protocol for <strong>{validationResult?.protocol_title}</strong> has been sent to:
              </p>
              <p className="text-blue-700 font-semibold mb-4">{email}</p>
              <p className="text-sm text-gray-500 mb-6">
                Don't see it? Check your spam folder.
              </p>
              <button
                onClick={resetForm}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors inline-flex items-center gap-2"
                data-testid="reset-form-button"
              >
                <RotateCcw className="w-4 h-4" />
                Use Another Code
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              {/* Step 1: Enter Code */}
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">1</span>
                  <label className="text-sm font-medium text-gray-700">Verification Code</label>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={verificationCode}
                    onChange={(e) => {
                      setVerificationCode(e.target.value.toUpperCase());
                      if (validationResult) {
                        setValidationResult(null);
                        setEmail('');
                        setPhone('');
                        setName('');
                        setSelectedLanguage(null);
                        setEmailError(null);
                      }
                    }}
                    placeholder="ZX-XXXXXX-XXXX-X-XXXXX"
                    disabled={validationResult?.valid}
                    className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm disabled:bg-gray-100"
                    data-testid="verification-code-input"
                    onKeyDown={(e) => { if (e.key === 'Enter' && !validationResult?.valid) validateCode(); }}
                  />
                  {validationResult?.valid ? (
                    <button
                      onClick={resetForm}
                      className="px-4 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors whitespace-nowrap text-sm"
                      data-testid="change-code-button"
                    >
                      Change
                    </button>
                  ) : (
                    <button
                      onClick={validateCode}
                      disabled={validating || !verificationCode.trim()}
                      className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold rounded-lg transition-colors whitespace-nowrap flex items-center gap-2 text-sm"
                      data-testid="validate-code-button"
                    >
                      {validating ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <ArrowRight className="w-4 h-4" />
                      )}
                      {validating ? 'Checking...' : 'Validate'}
                    </button>
                  )}
                </div>

                {/* Validation Result */}
                {validationResult && !validationResult.valid && (
                  <div className="mt-3 rounded-lg p-3 bg-red-50 border border-red-200" data-testid="validation-error">
                    <p className="text-sm text-red-700 flex items-start gap-2">
                      <X className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      {validationResult.message}
                    </p>
                  </div>
                )}

                {/* Validated Protocol Info */}
                {validationResult?.valid && (
                  <div className="mt-3 rounded-lg p-3 bg-green-50 border border-green-200" data-testid="validation-success">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-green-800">{validationResult.message}</p>
                        <p className="text-sm text-green-700 mt-1">
                          <strong>{validationResult.protocol_title}</strong> - {validationResult.duration_weeks} weeks
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Step 2: Contact Info (shown after validation) */}
              {validationResult?.valid && (
                <div className="p-6 border-b border-gray-100">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">2</span>
                    <label className="text-sm font-medium text-gray-700">Your Contact Info</label>
                  </div>
                  <div className="space-y-3">
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="your@email.com *"
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                        data-testid="email-input"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="text"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          placeholder="Your name"
                          className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          data-testid="name-input"
                        />
                      </div>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          placeholder="+1 (555) 000-0000"
                          className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          data-testid="phone-input"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Language Selection */}
              {validationResult?.valid && (
                <div className="p-6 border-b border-gray-100" data-testid="language-selection">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">3</span>
                    <label className="text-sm font-medium text-gray-700">Select Language</label>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { code: 'en', label: 'English' },
                      { code: 'es', label: 'Espanol' },
                      { code: 'pt', label: 'Portugues' }
                    ].map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => setSelectedLanguage(lang.code)}
                        className={`p-3 rounded-lg border-2 transition-colors text-center ${
                          selectedLanguage === lang.code
                            ? 'border-blue-600 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300 text-gray-700'
                        }`}
                        data-testid={`lang-${lang.code}`}
                      >
                        <Globe className="w-5 h-5 mx-auto mb-1" />
                        <span className="text-sm font-medium">{lang.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Error + Submit */}
              {validationResult?.valid && (
                <div className="p-6">
                  {emailError && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                      <p className="text-sm text-red-700">{emailError}</p>
                    </div>
                  )}

                  <button
                    onClick={sendProtocol}
                    disabled={sending || !email.trim() || !selectedLanguage}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                    data-testid="send-protocol-button"
                  >
                    {sending ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Sending...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5" />
                        <span>Send Protocol to Email</span>
                      </>
                    )}
                  </button>

                  <p className="mt-3 text-xs text-gray-500 text-center">
                    The PDF will be watermarked with your email for traceability. By submitting, you agree to receive the protocol from Zurix Sciences.
                  </p>
                </div>
              )}
            </div>
          )}
          </div>
        </div>

        {/* Paid Protocols Section */}
        {paidProtocols.length > 0 && (
          <div>
            <div className="flex items-center gap-3 mb-6">
              <Lock className="w-6 h-6 text-purple-600" />
              <h2 className="text-2xl font-bold text-gray-900">Advanced Protocols</h2>
              <span className="bg-purple-100 text-purple-800 text-sm px-3 py-1 rounded-full">Premium</span>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-6">
              <p className="text-purple-800 text-sm">
                <strong>Advanced protocols</strong> include in-depth research, optimized dosing schedules, and professional-grade information. Payment via USDT (TRC20).
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {paidProtocols.map((protocol) => (
                <div
                  key={protocol.id}
                  className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow border-2 border-purple-200 overflow-hidden cursor-pointer"
                  onClick={() => openPaidProtocol(protocol)}
                  data-testid={`protocol-card-${protocol.id}`}
                >
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                        {protocol.category}
                      </span>
                      <span className="text-purple-600 font-bold text-lg">
                        ${protocol.price}
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
                  <div className="px-6 py-3 bg-purple-50 border-t border-purple-100">
                    <button className="w-full text-purple-600 font-semibold text-sm hover:text-purple-700 flex items-center justify-center gap-2">
                      <CreditCard className="w-4 h-4" />
                      Purchase Protocol
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Paid Protocol Modal */}
      {selectedPaidProtocol && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto" data-testid="paid-protocol-modal">
            <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{selectedPaidProtocol.title}</h3>
                <span className="text-purple-600 font-bold">${selectedPaidProtocol.price} USDT</span>
              </div>
              <button
                onClick={closePaidModal}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                data-testid="close-paid-modal-button"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6">
              {/* Success */}
              {paidEmailSent ? (
                <div className="text-center py-8" data-testid="paid-email-sent-success">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Payment Confirmed!</h3>
                  <p className="text-gray-600 mb-4">
                    Check your email at <strong>{paidEmail}</strong> for the protocol PDF.
                  </p>
                  <button
                    onClick={closePaidModal}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                  >
                    Close
                  </button>
                </div>
              ) : paymentOrder ? (
                /* Payment Flow */
                <div data-testid="payment-flow">
                  <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-4">
                    <p className="text-purple-800 font-medium mb-2">Order #{paymentOrder.order_id}</p>
                    <p className="text-purple-700 text-sm">Amount: <strong>${paymentOrder.price} USDT</strong></p>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-4 mb-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Send USDT (TRC20) to:</p>
                    <div className="flex items-center gap-2 bg-white border border-gray-300 rounded-lg p-3">
                      <code className="text-sm text-gray-800 flex-1 break-all">{paymentOrder.wallet_address}</code>
                      <button
                        onClick={() => copyToClipboard(paymentOrder.wallet_address)}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Copy address"
                      >
                        <Copy className={`w-4 h-4 ${copied ? 'text-green-600' : 'text-gray-500'}`} />
                      </button>
                    </div>
                    {copied && <p className="text-green-600 text-xs mt-1">Copied!</p>}
                    <p className="text-xs text-gray-500 mt-2">Network: TRC20 (Tron)</p>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                    <p className="text-yellow-800 text-sm">
                      <strong>Important:</strong> Send exactly ${paymentOrder.price} USDT. After sending, enter the transaction ID (TXID) below.
                    </p>
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Transaction ID (TXID)
                    </label>
                    <input
                      type="text"
                      value={txid}
                      onChange={(e) => setTxid(e.target.value)}
                      placeholder="Enter your TXID after payment..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
                      data-testid="txid-input"
                    />
                    <a
                      href="https://tronscan.org/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 mt-1"
                    >
                      Find your TXID on TronScan <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>

                  {paymentResult && !paymentResult.paid && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                      <p className="text-red-700 text-sm">{paymentResult.message}</p>
                    </div>
                  )}

                  <button
                    onClick={verifyPayment}
                    disabled={verifyingPayment || !txid.trim()}
                    className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                    data-testid="verify-payment-button"
                  >
                    {verifyingPayment ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Verifying...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-5 h-5" />
                        <span>Verify Payment</span>
                      </>
                    )}
                  </button>
                </div>
              ) : (
                /* Paid Protocol Contact Form */
                <>
                  <p className="text-gray-600 mb-4">{selectedPaidProtocol.description}</p>
                  <div className="flex items-center gap-4 mb-6">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Clock className="w-4 h-4" />
                      <span>{selectedPaidProtocol.duration_weeks} weeks</span>
                    </div>
                    <span className="text-purple-600 font-semibold text-sm">${selectedPaidProtocol.price} USDT</span>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-4 mb-4">
                    <label className="text-sm font-medium text-gray-700 mb-3 block">Your Contact Info</label>
                    <div className="space-y-3">
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="email"
                          value={paidEmail}
                          onChange={(e) => setPaidEmail(e.target.value)}
                          placeholder="your@email.com *"
                          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                          data-testid="paid-email-input"
                          required
                        />
                      </div>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="tel"
                          value={paidPhone}
                          onChange={(e) => setPaidPhone(e.target.value)}
                          placeholder="+1 (555) 000-0000"
                          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                          data-testid="paid-phone-input"
                        />
                      </div>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="text"
                          value={paidName}
                          onChange={(e) => setPaidName(e.target.value)}
                          placeholder="Your name (optional)"
                          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                          data-testid="paid-name-input"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-4 mb-4" data-testid="paid-language-selection">
                    <label className="text-sm font-medium text-gray-700 mb-3 block">Select Language</label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { code: 'en', label: 'English' },
                        { code: 'es', label: 'Espanol' },
                        { code: 'pt', label: 'Portugues' }
                      ].map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => setPaidLanguage(lang.code)}
                          className={`p-3 rounded-lg border-2 transition-colors text-center ${
                            paidLanguage === lang.code
                              ? 'border-purple-600 bg-purple-50 text-purple-700'
                              : 'border-gray-200 hover:border-gray-300 text-gray-700'
                          }`}
                          data-testid={`paid-lang-${lang.code}`}
                        >
                          <Globe className="w-5 h-5 mx-auto mb-1" />
                          <span className="text-sm font-medium">{lang.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {paidEmailError && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                      <p className="text-sm text-red-700">{paidEmailError}</p>
                    </div>
                  )}

                  <button
                    onClick={createPaymentOrder}
                    disabled={paidSending || !paidEmail.trim() || !paidLanguage}
                    className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                    data-testid="paid-submit-button"
                  >
                    {paidSending ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        <CreditCard className="w-5 h-5" />
                        <span>Continue to Payment (${selectedPaidProtocol.price})</span>
                      </>
                    )}
                  </button>

                  <p className="mt-3 text-xs text-gray-500 text-center">
                    Payment via USDT (TRC20). Protocol delivered instantly after confirmation.
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Protocols;

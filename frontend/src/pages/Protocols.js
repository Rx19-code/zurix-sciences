import React, { useState, useEffect } from 'react';
import { FileText, Clock, X, CheckCircle, Globe, Lock, Unlock, Mail, Phone, User, Send, Loader2, CreditCard, Copy, ExternalLink } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Protocols = () => {
  const [protocols, setProtocols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [batchNumber, setBatchNumber] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  
  // Email form state
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  const [sending, setSending] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [emailError, setEmailError] = useState(null);
  
  // Payment state
  const [paymentOrder, setPaymentOrder] = useState(null);
  const [txid, setTxid] = useState('');
  const [verifyingPayment, setVerifyingPayment] = useState(false);
  const [paymentResult, setPaymentResult] = useState(null);
  const [copied, setCopied] = useState(false);

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
    setEmail('');
    setPhone('');
    setName('');
    setSelectedLanguage(null);
    setEmailSent(false);
    setEmailError(null);
    setPaymentOrder(null);
    setTxid('');
    setPaymentResult(null);
  };

  const closeModal = () => {
    setSelectedProtocol(null);
    setBatchNumber('');
    setValidationResult(null);
    setEmail('');
    setPhone('');
    setName('');
    setSelectedLanguage(null);
    setEmailSent(false);
    setEmailError(null);
    setPaymentOrder(null);
    setTxid('');
    setPaymentResult(null);
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

  const sendProtocolEmail = async () => {
    if (!email.trim() || !selectedLanguage) return;
    
    setSending(true);
    setEmailError(null);
    
    try {
      const response = await fetch(`${API}/protocols-v2/send-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protocol_id: selectedProtocol.id,
          batch_number: batchNumber.trim(),
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
        setEmailError(data.detail || 'Failed to send email. Please try again.');
      }
    } catch (error) {
      console.error('Error sending protocol email:', error);
      setEmailError('Network error. Please check your connection and try again.');
    } finally {
      setSending(false);
    }
  };

  // Create payment order for paid protocols
  const createPaymentOrder = async () => {
    if (!email.trim() || !selectedLanguage) return;
    
    setSending(true);
    setEmailError(null);
    
    try {
      const response = await fetch(`${API}/payment/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protocol_id: selectedProtocol.id,
          language: selectedLanguage,
          email: email.trim(),
          phone: phone.trim() || null,
          name: name.trim() || null
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setPaymentOrder(data);
      } else {
        setEmailError(data.detail || 'Failed to create order. Please try again.');
      }
    } catch (error) {
      console.error('Error creating payment order:', error);
      setEmailError('Network error. Please try again.');
    } finally {
      setSending(false);
    }
  };

  // Verify USDT payment
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
        setEmailSent(true);
      }
    } catch (error) {
      console.error('Error verifying payment:', error);
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

  // Separate protocols into free and paid
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
        
        {/* Free Protocols Section */}
        <div className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <Unlock className="w-6 h-6 text-green-600" />
            <h2 className="text-2xl font-bold text-gray-900">Free Protocols</h2>
            <span className="bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full">With valid batch number</span>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <p className="text-blue-800 text-sm">
              <strong>How it works:</strong> Purchase any Zurix Sciences product → Find the batch number on your label → Enter it to unlock the corresponding protocol for free.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {freeProtocols.map((protocol) => (
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
                    <Mail className="w-4 h-4" />
                    Get Protocol
                  </button>
                </div>
              </div>
            ))}
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
                  onClick={() => openProtocol(protocol)}
                  data-testid={`protocol-card-${protocol.id}`}
                >
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getCategoryColor(protocol.category)}`}>
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

      {/* Protocol Modal */}
      {selectedProtocol && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto" data-testid="protocol-modal">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{selectedProtocol.title}</h3>
                {selectedProtocol.price > 0 && (
                  <span className="text-purple-600 font-bold">${selectedProtocol.price} USDT</span>
                )}
              </div>
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
              {/* Success State */}
              {emailSent ? (
                <div className="text-center py-8" data-testid="email-sent-success">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {selectedProtocol.price > 0 ? 'Payment Confirmed!' : 'Protocol Sent!'}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Check your email at <strong>{email}</strong> for the protocol PDF.
                  </p>
                  <p className="text-sm text-gray-500 mb-6">
                    Don't see it? Check your spam folder.
                  </p>
                  <button
                    onClick={closeModal}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                  >
                    Close
                  </button>
                </div>
              ) : paymentOrder ? (
                /* Payment Flow for Paid Protocols */
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
                /* Initial Form */
                <>
                  <p className="text-gray-600 mb-4">{selectedProtocol.description}</p>
                  
                  <div className="flex items-center gap-4 mb-6">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Clock className="w-4 h-4" />
                      <span>{selectedProtocol.duration_weeks} weeks</span>
                    </div>
                    {selectedProtocol.price > 0 ? (
                      <span className="text-purple-600 font-semibold text-sm">${selectedProtocol.price} USDT</span>
                    ) : (
                      <span className="text-green-600 font-semibold text-sm">FREE with valid batch</span>
                    )}
                  </div>

                  {/* Step 1: Batch Validation (only for free protocols) */}
                  {selectedProtocol.requires_batch && (
                    <div className="bg-gray-50 rounded-xl p-4 mb-4">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">1</span>
                        <label className="text-sm font-medium text-gray-700">Product Batch Number</label>
                      </div>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={batchNumber}
                          onChange={(e) => setBatchNumber(e.target.value.toUpperCase())}
                          placeholder="ZX-XXXXXX-XXXX-X"
                          disabled={validationResult?.valid}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm disabled:bg-gray-100"
                          data-testid="batch-number-input"
                        />
                        {!validationResult?.valid && (
                          <button
                            onClick={validateBatch}
                            disabled={validating || !batchNumber.trim()}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold rounded-lg transition-colors whitespace-nowrap"
                            data-testid="validate-batch-button"
                          >
                            {validating ? 'Checking...' : 'Validate'}
                          </button>
                        )}
                      </div>
                    </div>
                  )}

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

                  {/* Contact Info (shown after batch validation for free, or immediately for paid) */}
                  {(validationResult?.valid || !selectedProtocol.requires_batch) && (
                    <>
                      {/* Contact Info */}
                      <div className="bg-gray-50 rounded-xl p-4 mb-4">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                            {selectedProtocol.requires_batch ? '2' : '1'}
                          </span>
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
                              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                              data-testid="email-input"
                              required
                            />
                          </div>
                          <div className="relative">
                            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <input
                              type="tel"
                              value={phone}
                              onChange={(e) => setPhone(e.target.value)}
                              placeholder="+1 (555) 000-0000"
                              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                              data-testid="phone-input"
                            />
                          </div>
                          <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <input
                              type="text"
                              value={name}
                              onChange={(e) => setName(e.target.value)}
                              placeholder="Your name (optional)"
                              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                              data-testid="name-input"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Language Selection */}
                      <div className="bg-gray-50 rounded-xl p-4 mb-4" data-testid="language-selection">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                            {selectedProtocol.requires_batch ? '3' : '2'}
                          </span>
                          <label className="text-sm font-medium text-gray-700">Select Language</label>
                        </div>
                        <div className="grid grid-cols-3 gap-2">
                          {['en', 'es', 'pt'].map((lang) => (
                            <button
                              key={lang}
                              onClick={() => setSelectedLanguage(lang)}
                              className={`p-3 rounded-lg border-2 transition-colors text-center ${
                                selectedLanguage === lang
                                  ? 'border-blue-600 bg-blue-50 text-blue-700'
                                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
                              }`}
                              data-testid={`lang-${lang}`}
                            >
                              <Globe className="w-5 h-5 mx-auto mb-1" />
                              <span className="text-sm font-medium">
                                {lang === 'en' ? 'English' : lang === 'es' ? 'Español' : 'Português'}
                              </span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Error Message */}
                      {emailError && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                          <p className="text-sm text-red-700">{emailError}</p>
                        </div>
                      )}

                      {/* Action Button */}
                      <button
                        onClick={selectedProtocol.price > 0 ? createPaymentOrder : sendProtocolEmail}
                        disabled={sending || !email.trim() || !selectedLanguage}
                        className={`w-full ${selectedProtocol.price > 0 ? 'bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300' : 'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300'} text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2`}
                        data-testid="submit-button"
                      >
                        {sending ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Processing...</span>
                          </>
                        ) : selectedProtocol.price > 0 ? (
                          <>
                            <CreditCard className="w-5 h-5" />
                            <span>Continue to Payment (${selectedProtocol.price})</span>
                          </>
                        ) : (
                          <>
                            <Send className="w-5 h-5" />
                            <span>Send Protocol to Email</span>
                          </>
                        )}
                      </button>
                      
                      <p className="mt-3 text-xs text-gray-500 text-center">
                        {selectedProtocol.price > 0 
                          ? 'Payment via USDT (TRC20). Protocol delivered instantly after confirmation.'
                          : 'By submitting, you agree to receive the protocol and occasional updates from Zurix Sciences.'
                        }
                      </p>
                    </>
                  )}
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

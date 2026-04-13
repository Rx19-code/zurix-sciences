import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Lock, Loader2, Layers, Target, Beaker, Zap } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

var API = process.env.REACT_APP_BACKEND_URL;

export default function StackDetail() {
  var params = useParams();
  var slug = params.slug;
  var navigate = useNavigate();
  var { user, token } = useAuth();
  var [stack, setStack] = useState(null);
  var [loading, setLoading] = useState(true);

  useEffect(function() {
    fetch(API + '/api/stacks/' + slug)
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.error) { navigate('/protocols'); return; }
        setStack(data);
        setLoading(false);
      })
      .catch(function() { navigate('/protocols'); });
  }, [slug, navigate]);

  if (loading || !stack) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  var pepList = stack.peptides || [];
  var howList = stack.how_to_use || [];
  var hasAccess = user && user.has_lifetime_access;

  return (
    <div className="min-h-screen bg-gray-50" data-testid="stack-detail-page">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-700 to-blue-800 px-4 sm:px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <button data-testid="back-to-library" onClick={function() { navigate('/protocols'); }} className="inline-flex items-center gap-1.5 text-purple-200 hover:text-white text-sm mb-4 transition-colors">
            <ChevronLeft className="w-4 h-4" />
            Back to Library
          </button>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="bg-white/15 border border-white/25 text-white text-xs font-medium px-2.5 py-1 rounded-full">{stack.category}</span>
            <span className="bg-purple-400/20 text-purple-200 border border-purple-300/30 text-xs font-semibold px-2.5 py-1 rounded-full flex items-center gap-1">
              <Layers className="w-3 h-3" /> Stack Protocol
            </span>
            <span className="bg-yellow-500/20 text-yellow-300 border border-yellow-400/30 text-xs font-semibold px-2.5 py-1 rounded-full">PRO</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2" data-testid="stack-name">{stack.name}</h1>
          <p className="text-purple-100 text-sm sm:text-base">{stack.goal}</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6">
        {/* Peptides included */}
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-5 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <Beaker className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-gray-900">Peptides in this Stack</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {pepList.map(function(p, i) {
              return <span key={i} className="bg-blue-50 text-blue-700 border border-blue-200 text-sm font-medium px-3 py-1.5 rounded-full">{p}</span>;
            })}
          </div>
        </div>

        {hasAccess ? (
          <>
            {/* Why it works */}
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-5 mb-5">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-5 h-5 text-yellow-500" />
                <h2 className="text-base font-bold text-gray-900">Why It Works</h2>
              </div>
              <p className="text-gray-600 leading-relaxed">{stack.why_it_works}</p>
            </div>

            {/* How to use */}
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-5 mb-5">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-5 h-5 text-green-600" />
                <h2 className="text-base font-bold text-gray-900">How to Use</h2>
              </div>
              <div className="space-y-3">
                {howList.map(function(step, i) {
                  return (
                    <div key={i} className="flex gap-3 items-start">
                      <span className="w-7 h-7 rounded-full bg-green-100 text-green-600 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">{i + 1}</span>
                      <p className="text-gray-600 text-sm pt-1">{step}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        ) : (
          <LockedStackContent navigate={navigate} user={user} token={token} />
        )}
      </div>
    </div>
  );
}

function LockedStackContent({ navigate, user, token }) {
  var [payLoading, setPayLoading] = useState(false);
  var [paymentData, setPaymentData] = useState(null);
  var [checking, setChecking] = useState(false);
  var [payStatus, setPayStatus] = useState('');

  function handleCreateInvoice() {
    setPayLoading(true);
    fetch(API + '/api/payment/create-invoice', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.already_paid) { window.location.reload(); return; }
        setPaymentData(data);
        setPayLoading(false);
      })
      .catch(function() { setPayLoading(false); });
  }

  function handleCheckPayment() {
    if (!paymentData) return;
    setChecking(true);
    fetch(API + '/api/payment/check/' + paymentData.payment_id, {
      headers: { 'Authorization': 'Bearer ' + token },
    })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        setPayStatus(data.status);
        if (data.has_lifetime_access) { window.location.reload(); }
        setChecking(false);
      })
      .catch(function() { setChecking(false); });
  }

  if (!user) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-8 text-center" data-testid="locked-stack">
        <Lock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-gray-900 mb-2">Premium Content</h3>
        <p className="text-gray-500 text-sm mb-5">Sign in to unlock full stack protocols.</p>
        <button onClick={function() { navigate('/login'); }} className="bg-blue-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
          Sign In to Unlock
        </button>
        <p className="text-xs text-gray-400 mt-3">$39.99 USDT — Lifetime access</p>
      </div>
    );
  }

  if (paymentData) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6" data-testid="payment-flow">
        <h3 className="text-lg font-bold text-gray-900 mb-4 text-center">Complete Payment</h3>
        <div className="bg-gray-50 rounded-lg p-4 mb-4 text-center">
          <p className="text-sm text-gray-500 mb-1">Send exactly</p>
          <p className="text-2xl font-bold text-gray-900">{paymentData.pay_amount} USDT</p>
          <p className="text-xs text-gray-400 mt-1">TRC20 Network</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <p className="text-xs text-gray-500 mb-1">To this address:</p>
          <p className="text-sm font-mono text-gray-900 break-all select-all bg-white p-2 rounded border">{paymentData.pay_address}</p>
        </div>
        <button onClick={handleCheckPayment} disabled={checking} className="w-full bg-green-600 text-white font-semibold py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
          {checking ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          {checking ? 'Checking...' : 'I have paid - Check Status'}
        </button>
        {payStatus && payStatus !== 'confirmed' && payStatus !== 'finished' && (
          <p className="text-sm text-yellow-600 text-center mt-3">Status: {payStatus}</p>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-8 text-center" data-testid="locked-stack">
      <Lock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
      <h3 className="text-lg font-bold text-gray-900 mb-2">Premium Content</h3>
      <p className="text-gray-500 text-sm mb-5">Unlock the full protocol details for all stacks and peptides.</p>
      <button onClick={handleCreateInvoice} disabled={payLoading} className="inline-flex items-center gap-2 bg-yellow-500 text-white font-semibold px-6 py-3 rounded-lg hover:bg-yellow-600 transition-colors disabled:opacity-50">
        {payLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
        {payLoading ? 'Creating invoice...' : 'Unlock Full Access — $39.99'}
      </button>
      <p className="text-xs text-gray-400 mt-3">One-time payment via USDT (TRC20)</p>
    </div>
  );
}

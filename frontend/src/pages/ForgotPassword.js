import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft } from 'lucide-react';

var API = process.env.REACT_APP_BACKEND_URL;

export default function ForgotPassword() {
  var [email, setEmail] = useState('');
  var [loading, setLoading] = useState(false);
  var [sent, setSent] = useState(false);
  var [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      var resp = await fetch(API + '/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email }),
      });
      var data = {};
      try { data = await resp.json(); } catch (e) { data = {}; }
      if (!resp.ok) {
        setError(data.detail || 'Failed to send reset email');
      } else {
        setSent(true);
      }
    } catch (err) {
      setError('Network error. Try again.');
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12" data-testid="forgot-password-page">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="text-2xl font-bold text-blue-600">Zurix Sciences</Link>
          <p className="text-gray-500 mt-1">Premium Research Compounds</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <Link to="/login" className="inline-flex items-center gap-1.5 text-gray-500 hover:text-blue-600 text-sm mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Sign In
          </Link>

          <h2 className="text-xl font-bold text-gray-900 mb-2">Forgot Password</h2>
          <p className="text-sm text-gray-500 mb-6">
            Enter your email and we'll send you a link to reset your password.
          </p>

          {sent ? (
            <div className="text-center">
              <div className="bg-green-50 border border-green-200 text-green-700 text-sm px-4 py-3 rounded-lg mb-4" data-testid="reset-sent-message">
                If an account exists for <strong>{email}</strong>, a reset link has been sent. Check your inbox (and spam folder).
              </div>
              <Link to="/login" className="text-blue-600 font-medium hover:underline text-sm">Back to Sign In</Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={function(e) { setEmail(e.target.value); }}
                    className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    placeholder="you@example.com"
                    required
                    data-testid="forgot-email-input"
                  />
                </div>
              </div>

              {error && (
                <div className="bg-red-50 text-red-600 text-sm px-4 py-2.5 rounded-lg" data-testid="forgot-error">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                data-testid="send-reset-btn"
                className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

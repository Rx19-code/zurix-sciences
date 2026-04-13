import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react';

var API = process.env.REACT_APP_BACKEND_URL;

export default function Login() {
  var navigate = useNavigate();
  var { login } = useAuth();
  var [isRegister, setIsRegister] = useState(false);
  var [email, setEmail] = useState('');
  var [password, setPassword] = useState('');
  var [name, setName] = useState('');
  var [showPass, setShowPass] = useState(false);
  var [error, setError] = useState('');
  var [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      var url = isRegister ? API + '/api/auth/register' : API + '/api/auth/login';
      var body = isRegister ? { email: email, password: password, name: name } : { email: email, password: password };

      var resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      var data = await resp.json();

      if (!resp.ok) {
        setError(data.detail || 'Something went wrong');
        setLoading(false);
        return;
      }

      login(data.user, data.token);
      navigate('/protocols');
    } catch (err) {
      setError('Connection error. Please try again.');
    }
    setLoading(false);
  }

  function handleGoogle() {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    var redirectUrl = window.location.origin + '/auth/callback';
    window.location.href = 'https://auth.emergentagent.com/?redirect=' + encodeURIComponent(redirectUrl);
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12" data-testid="login-page">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="text-2xl font-bold text-blue-600">Zurix Sciences</Link>
          <p className="text-gray-500 mt-1">Premium Research Compounds</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 text-center" data-testid="auth-title">
            {isRegister ? 'Create Account' : 'Sign In'}
          </h2>

          {/* Google Login */}
          <button
            onClick={handleGoogle}
            data-testid="google-login-btn"
            className="w-full flex items-center justify-center gap-3 border border-gray-300 rounded-lg px-4 py-3 text-gray-700 font-medium hover:bg-gray-50 transition-colors mb-6"
          >
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </button>

          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-xs text-gray-400 uppercase">or</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>

          {/* Email/Password Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={name}
                    onChange={function(e) { setName(e.target.value); }}
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    placeholder="Your name"
                    required
                    data-testid="register-name-input"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={function(e) { setEmail(e.target.value); }}
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="your@email.com"
                  required
                  data-testid="email-input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={function(e) { setPassword(e.target.value); }}
                  className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="Min. 6 characters"
                  minLength={6}
                  required
                  data-testid="password-input"
                />
                <button type="button" onClick={function() { setShowPass(!showPass); }} className="absolute right-3 top-3 text-gray-400">
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 text-red-600 text-sm px-4 py-2.5 rounded-lg" data-testid="auth-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              data-testid="auth-submit-btn"
              className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In')}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            {isRegister ? 'Already have an account? ' : "Don't have an account? "}
            <button
              onClick={function() { setIsRegister(!isRegister); setError(''); }}
              className="text-blue-600 font-medium hover:underline"
              data-testid="toggle-auth-mode"
            >
              {isRegister ? 'Sign In' : 'Create Account'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  var [user, setUser] = useState(null);
  var [token, setToken] = useState(localStorage.getItem('zurix_token'));
  var [loading, setLoading] = useState(true);

  var checkAuth = useCallback(async function() {
    // CRITICAL: If returning from OAuth callback, skip the /me check.
    // AuthCallback will exchange the session_id and establish the session first.
    if (window.location.hash && window.location.hash.includes('session_id=')) {
      setLoading(false);
      return;
    }

    var saved = localStorage.getItem('zurix_token');
    if (!saved) {
      setLoading(false);
      return;
    }

    try {
      var resp = await fetch(API + '/api/auth/me', {
        headers: { 'Authorization': 'Bearer ' + saved }
      });
      if (resp.ok) {
        var data = await resp.json();
        setUser(data.user);
        setToken(saved);
      } else {
        localStorage.removeItem('zurix_token');
        setToken(null);
        setUser(null);
      }
    } catch (e) {
      console.error('Auth check failed:', e);
    }
    setLoading(false);
  }, []);

  useEffect(function() {
    checkAuth();
  }, [checkAuth]);

  var login = function(userData, jwtToken) {
    localStorage.setItem('zurix_token', jwtToken);
    setToken(jwtToken);
    setUser(userData);
  };

  var logout = function() {
    localStorage.removeItem('zurix_token');
    setToken(null);
    setUser(null);
  };

  var refreshUser = async function() {
    var saved = localStorage.getItem('zurix_token');
    if (!saved) return;
    try {
      var resp = await fetch(API + '/api/auth/me', {
        headers: { 'Authorization': 'Bearer ' + saved }
      });
      if (resp.ok) {
        var data = await resp.json();
        setUser(data.user);
      }
    } catch (e) {}
  };

  return React.createElement(AuthContext.Provider, {
    value: { user: user, token: token, loading: loading, login: login, logout: logout, refreshUser: refreshUser }
  }, children);
}

export function useAuth() {
  var ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}

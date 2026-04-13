import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

var API = process.env.REACT_APP_BACKEND_URL;

export default function AuthCallback() {
  var navigate = useNavigate();
  var { login } = useAuth();
  var hasProcessed = useRef(false);

  useEffect(function() {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    var hash = window.location.hash;
    var sessionId = null;

    if (hash && hash.includes('session_id=')) {
      var params = new URLSearchParams(hash.substring(1));
      sessionId = params.get('session_id');
    }

    if (!sessionId) {
      navigate('/login');
      return;
    }

    fetch(API + '/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.success) {
          login(data.user, data.token);
          navigate('/protocols');
        } else {
          navigate('/login');
        }
      })
      .catch(function() {
        navigate('/login');
      });
  }, [navigate, login]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Signing in with Google...</p>
      </div>
    </div>
  );
}

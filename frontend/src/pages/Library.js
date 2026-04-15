import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Library() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4" data-testid="library-page">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-3">Protocol Library</h1>
        <p className="text-gray-500 mb-2">This section is currently under maintenance.</p>
        <p className="text-gray-400 text-sm mb-6">We are updating our protocols and will be back shortly.</p>
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}

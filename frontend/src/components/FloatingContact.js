import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { MessageCircle, X, Shield } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const flagCode = { Paraguay: 'py', 'United States': 'us', Switzerland: 'ch' };

export default function FloatingContact() {
  const [open, setOpen] = useState(false);
  const [reps, setReps] = useState([]);
  const [productName, setProductName] = useState('');
  const location = useLocation();

  useEffect(() => {
    axios.get(`${API}/representatives`).then(r => setReps(r.data || [])).catch(() => {});
  }, []);

  useEffect(() => {
    const m = location.pathname.match(/^\/products\/([^/]+)$/);
    if (!m) { setProductName(''); return; }
    axios.get(`${API}/products/${m[1]}`)
      .then(r => setProductName(r.data?.name || ''))
      .catch(() => setProductName(''));
  }, [location.pathname]);

  const message = productName
    ? `Hello! I'm interested in ${productName} — https://zurixsciences.com${location.pathname}`
    : 'Hello! I am interested in Zurix Sciences products.';

  const openWhatsApp = (whatsapp) => {
    window.open(`https://wa.me/${whatsapp.replace(/\D/g, '')}?text=${encodeURIComponent(message)}`, '_blank');
  };
  const openThreema = (id) => window.open(`https://threema.id/${id}`, '_blank');

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col items-end gap-3">
      {open && (
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 w-80 overflow-hidden" data-testid="floating-contact-panel">
          <div className="bg-gray-900 px-4 py-3 flex items-center justify-between">
            <div>
              <p className="text-white font-semibold text-sm">Contact a Representative</p>
              {productName && <p className="text-gray-400 text-xs mt-0.5 truncate max-w-[220px]">About: {productName}</p>}
            </div>
            <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-white transition" data-testid="floating-contact-close">
              <X size={18} />
            </button>
          </div>
          <div className="divide-y divide-gray-100">
            {reps.map(rep => (
              <div key={rep.id} className="px-4 py-3 flex items-center gap-3" data-testid={`floating-rep-${flagCode[rep.country] || 'xx'}`}>
                <img
                  src={`https://flagcdn.com/w40/${flagCode[rep.country] || 'un'}.png`}
                  alt={rep.country}
                  className="w-8 h-6 rounded object-cover shadow-sm flex-shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-gray-900 text-sm font-medium">{rep.country}</p>
                  <p className="text-gray-500 text-xs truncate">{rep.region}</p>
                </div>
                {rep.whatsapp && (
                  <button
                    onClick={() => openWhatsApp(rep.whatsapp)}
                    className="flex items-center gap-1.5 bg-green-500 hover:bg-green-600 text-white text-xs font-semibold px-3 py-2 rounded-lg transition"
                    data-testid={`floating-whatsapp-${flagCode[rep.country] || 'xx'}`}
                  >
                    <MessageCircle size={14} /> WhatsApp
                  </button>
                )}
                {rep.threema && (
                  <button
                    onClick={() => openThreema(rep.threema)}
                    className="flex items-center gap-1.5 bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold px-3 py-2 rounded-lg transition"
                    data-testid="floating-threema-ch"
                  >
                    <Shield size={14} /> Threema
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      <button
        onClick={() => setOpen(!open)}
        className="w-14 h-14 rounded-full bg-green-500 hover:bg-green-600 text-white shadow-xl flex items-center justify-center transition-transform hover:scale-105"
        aria-label="Contact us"
        data-testid="floating-contact-btn"
      >
        {open ? <X size={26} /> : <MessageCircle size={26} />}
      </button>
    </div>
  );
}

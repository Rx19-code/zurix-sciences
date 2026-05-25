import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeft, X, Beaker, Target, Users, FlaskConical, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import StarRating from '../components/StarRating';

var API = process.env.REACT_APP_BACKEND_URL;

export default function HubDetail() {
  var params = useParams();
  var slug = params.slug;
  var navigate = useNavigate();
  var { user } = useAuth();
  var [hub, setHub] = useState(null);
  var [loading, setLoading] = useState(true);
  var [selectedProtocol, setSelectedProtocol] = useState(null);

  useEffect(() => {
    fetch(API + '/api/hubs/' + slug)
      .then(r => r.json())
      .then(data => {
        if (data.error) { navigate('/protocols'); return; }
        setHub(data);
        setLoading(false);
      })
      .catch(() => navigate('/protocols'));
  }, [slug, navigate]);

  if (loading || !hub) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  var hasAccess = user && user.has_lifetime_access;

  if (!hasAccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-purple-100 rounded-full mb-3">
            <Sparkles className="w-7 h-7 text-purple-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Premium Stack Hub</h2>
          <p className="text-sm text-gray-500 mb-6">Unlock {hub.title} and all Premium protocols with Lifetime Access ($39.99 USDT).</p>
          <Link to="/login" className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors" data-testid="hub-paywall-cta">
            Sign In to Unlock
          </Link>
        </div>
      </div>
    );
  }

  var protocolsList = hub.protocols || [];
  var coreInfo = hub.core_info || {};
  var pairings = coreInfo.common_pairings || [];

  return (
    <div className="min-h-screen bg-gray-50" data-testid="hub-detail-page">
      {/* Hero */}
      <div className="bg-gradient-to-br from-purple-700 via-purple-800 to-indigo-900 text-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
          <button onClick={() => navigate('/protocols')} className="inline-flex items-center gap-1.5 text-purple-200 hover:text-white text-sm mb-4 transition-colors" data-testid="back-to-library">
            <ChevronLeft className="w-4 h-4" />
            Back to Library
          </button>
          <div className="flex items-center gap-2 mb-3">
            <span className="bg-white/15 border border-white/25 text-white text-xs font-semibold px-2.5 py-1 rounded-full">{protocolsList.length} Protocols</span>
            <span className="bg-yellow-500/20 border border-yellow-300/30 text-yellow-200 text-xs font-semibold px-2.5 py-1 rounded-full">PREMIUM</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-bold mb-1" data-testid="hub-title">{hub.title}</h1>
          <p className="text-sm sm:text-base text-purple-200 mb-3 uppercase tracking-wider">{hub.subtitle}</p>
          <p className="text-sm sm:text-base text-purple-100 max-w-3xl">{hub.description}</p>
        </div>
      </div>

      {/* Core Info */}
      {Object.keys(coreInfo).length > 0 && (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-8">
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-purple-600" />
            {hub.peptide_name} — Core Information
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            {coreInfo.function && <InfoBlock label="Function" value={coreInfo.function} />}
            {coreInfo.typical_dosage && <InfoBlock label="Typical Dosage" value={coreInfo.typical_dosage} />}
            {coreInfo.administration && <InfoBlock label="Administration" value={coreInfo.administration} />}
            {coreInfo.best_timing && <InfoBlock label="Best Timing" value={coreInfo.best_timing} />}
            {coreInfo.common_cycle && <InfoBlock label="Common Cycle Length" value={coreInfo.common_cycle} />}
          </div>
          {pairings.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Common Pairings</p>
              <div className="flex flex-wrap gap-1.5">
                {pairings.map((p, i) => (
                  <span key={i} className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full">{p}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      )}

      {/* Protocols Grid */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          {protocolsList.length} Protocol Variations
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="protocols-grid">
          {protocolsList.map(function(p, idx) {
            var compounds = p.compounds || [];
            return (
              <div
                key={p.id}
                onClick={() => setSelectedProtocol(p)}
                className="bg-white border border-gray-200 rounded-xl p-5 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-purple-100/60 hover:border-purple-200 relative overflow-hidden flex flex-col"
                data-testid={`protocol-card-${p.id}`}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-bl from-purple-50 to-transparent rounded-bl-full" />
                <div className="flex items-start justify-between mb-3 relative">
                  <div className="w-9 h-9 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-bold text-sm shrink-0">{idx + 1}</div>
                  <span className="bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full">Protocol</span>
                </div>
                <h3 className="text-base font-bold text-gray-900 mb-1 leading-snug">{p.name}</h3>
                <p className="text-gray-500 text-sm mb-4 line-clamp-2 flex-1">{p.goal}</p>

                {/* Compounds chips */}
                {compounds.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {compounds.slice(0, 3).map(function(c, i) {
                      return (
                        <span key={i} className="text-[11px] bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full font-medium">
                          {c.name}
                        </span>
                      );
                    })}
                    {compounds.length > 3 && (
                      <span className="text-[11px] text-gray-500 px-1">+{compounds.length - 3}</span>
                    )}
                  </div>
                )}

                {/* Rating */}
                <div onClick={(e) => e.stopPropagation()} className="pt-3 border-t border-gray-100">
                  <StarRating hubSlug={hub.slug} protocolId={p.id} initialAvg={p.rating_avg || 0} initialCount={p.rating_count || 0} size="sm" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Modal de detalhe */}
      {selectedProtocol && (
        <ProtocolModal
          protocol={selectedProtocol}
          hubSlug={hub.slug}
          onClose={() => setSelectedProtocol(null)}
          index={protocolsList.findIndex(x => x.id === selectedProtocol.id) + 1}
        />
      )}
    </div>
  );
}

function ProtocolModal({ protocol, hubSlug, onClose, index }) {
  // Close on Escape key
  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape') onClose(); }
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto" onClick={onClose} data-testid="protocol-modal">
      <div className="bg-white rounded-t-2xl sm:rounded-2xl w-full max-w-2xl my-0 sm:my-8 max-h-[95vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {/* Header sticky */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-5 sm:px-6 py-4 flex items-start justify-between gap-3 z-10">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-bold shrink-0">{index}</div>
            <div className="min-w-0">
              <h3 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">{protocol.name}</h3>
              <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{protocol.goal}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg shrink-0" data-testid="modal-close">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Body */}
        <div className="px-5 sm:px-6 py-5 space-y-5">
          <ProtocolSection icon={<Target className="w-4 h-4" />} title="Goal">
            <p className="text-gray-700 text-sm">{protocol.goal}</p>
          </ProtocolSection>

          <ProtocolSection icon={<Beaker className="w-4 h-4" />} title="Compounds">
            <ul className="space-y-2">
              {(protocol.compounds || []).map(function(c, i) {
                return (
                  <li key={i} className="flex items-start gap-2.5 text-sm bg-gray-50 px-3 py-2 rounded-lg">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                    <div className="flex-1 flex flex-wrap justify-between gap-2">
                      <span className="font-semibold text-gray-900">{c.name}</span>
                      <span className="text-gray-600 font-medium">{c.dose}</span>
                    </div>
                  </li>
                );
              })}
            </ul>
          </ProtocolSection>

          <ProtocolSection icon={<Sparkles className="w-4 h-4" />} title="Protocol">
            <ol className="space-y-2">
              {(protocol.protocol || []).map(function(step, i) {
                return (
                  <li key={i} className="flex items-start gap-2.5 text-sm text-gray-700">
                    <span className="w-6 h-6 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0">{i + 1}</span>
                    <span className="pt-0.5">{step}</span>
                  </li>
                );
              })}
            </ol>
          </ProtocolSection>

          <ProtocolSection icon={<Users className="w-4 h-4" />} title="Best For">
            <p className="text-gray-700 text-sm">{protocol.best_for}</p>
          </ProtocolSection>

          {/* Rating block */}
          <div className="pt-4 border-t border-gray-100">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Rate This Protocol</h4>
            <StarRating hubSlug={hubSlug} protocolId={protocol.id} initialAvg={protocol.rating_avg || 0} initialCount={protocol.rating_count || 0} size="lg" />
            <p className="text-xs text-gray-400 mt-2">Your vote helps the community discover the most effective protocols.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoBlock({ label, value }) {
  return (
    <div>
      <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-0.5">{label}</p>
      <p className="text-sm text-gray-900">{value}</p>
    </div>
  );
}

function ProtocolSection({ icon, title, children }) {
  return (
    <div>
      <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
        {icon} {title}
      </h4>
      {children}
    </div>
  );
}

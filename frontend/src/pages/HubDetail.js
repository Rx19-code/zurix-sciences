import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeft, X, Beaker, Target, Users, FlaskConical, Sparkles, Clock, Syringe, Flame, Star, List } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import StarRating from '../components/StarRating';
import { calculateUI } from '../utils/peptideUI';

var API = process.env.REACT_APP_BACKEND_URL;

// Bayesian average for trending — prevents 1 vote (5★) from beating 50 votes (4.8★)
function trendingScore(p, globalAvg, minVotes) {
  var v = p.rating_count || 0;
  var avg = p.rating_avg || 0;
  return (v * avg + minVotes * globalAvg) / (v + minVotes || 1);
}

function sortProtocols(list, mode) {
  if (!list || !list.length) return [];
  var rated = list.filter(p => (p.rating_count || 0) > 0);
  if (mode === 'default' || rated.length === 0) {
    return [...list].sort((a, b) => (a.order || 0) - (b.order || 0));
  }
  // Global avg for Bayesian smoothing
  var totalVotes = rated.reduce((s, p) => s + (p.rating_count || 0), 0);
  var globalAvg = totalVotes ? rated.reduce((s, p) => s + (p.rating_avg || 0) * (p.rating_count || 0), 0) / totalVotes : 4.5;
  var minVotes = 10;
  if (mode === 'trending') {
    return [...list].sort((a, b) => trendingScore(b, globalAvg, minVotes) - trendingScore(a, globalAvg, minVotes));
  }
  if (mode === 'top') {
    return [...list].sort((a, b) => {
      var diff = (b.rating_avg || 0) - (a.rating_avg || 0);
      if (Math.abs(diff) > 0.01) return diff;
      return (b.rating_count || 0) - (a.rating_count || 0);
    });
  }
  return list;
}

export default function HubDetail() {
  var params = useParams();
  var slug = params.slug;
  var navigate = useNavigate();
  var { user } = useAuth();
  var [hub, setHub] = useState(null);
  var [loading, setLoading] = useState(true);
  var [selectedProtocol, setSelectedProtocol] = useState(null);
  var [sortMode, setSortMode] = useState('default');

  useEffect(() => {
    fetch(API + '/api/hubs/' + slug)
      .then(r => r.json())
      .then(data => {
        if (data.error) { navigate('/protocols'); return; }
        setHub(data);
        setLoading(false);
      })
      .catch(() => navigate('/protocols'));
    // API is a module-level constant from process.env; safe to omit
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug, navigate]);

  // Hooks must run unconditionally — derive memoized lists from hub (may be null during loading)
  var protocolsListMemo = (hub && hub.protocols) || [];
  var sortedProtocols = useMemo(() => sortProtocols(protocolsListMemo, sortMode), [protocolsListMemo, sortMode]);
  var trendingTopIds = useMemo(() => {
    var ranked = sortProtocols(protocolsListMemo, 'trending').slice(0, 3);
    return new Set(ranked.map(p => p.id));
  }, [protocolsListMemo]);

  if (loading || !hub) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  var hasAccess = user && user.has_lifetime_access;

  if (!hasAccess) {
    var heroImgPaywall = API + '/api/hubs/hero-image/' + (hub.peptide_slug || hub.slug || '');
    var previewProtocols = (hub.protocols || []).slice(0, 6);
    var totalProtocols = (hub.protocols || []).length;
    var hubCoreInfo = hub.core_info || {};
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Hero — same as paid version, fully visible */}
        <div className="relative h-72 sm:h-80 bg-gradient-to-br from-purple-900 to-blue-900 overflow-hidden">
          <img src={heroImgPaywall} alt="" className="w-full h-full object-cover opacity-50" onError={(e) => { e.target.style.display = 'none'; }} />
          <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-transparent" />
          <div className="absolute inset-x-0 bottom-0 px-4 sm:px-6 py-6">
            <div className="max-w-6xl mx-auto">
              <div className="inline-flex items-center gap-1.5 bg-yellow-500/90 text-yellow-950 text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full mb-3">
                <Sparkles className="w-3.5 h-3.5" /> Premium Stack Hub
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold text-white drop-shadow-lg" data-testid="hub-title-locked">{hub.peptide_name || hub.title}</h1>
              <p className="text-purple-200 text-sm mt-1">{hub.subtitle}</p>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
          {/* Description — visible */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
            <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">About {hub.peptide_name}</h2>
            <p className="text-gray-700 text-sm leading-relaxed">{hub.description}</p>
            {hubCoreInfo.mechanism && (
              <p className="text-gray-500 text-xs mt-3 italic"><strong>Mechanism:</strong> {hubCoreInfo.mechanism}</p>
            )}
          </div>

          {/* Protocols preview — blurred names */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                {totalProtocols} Premium Protocols Inside
              </h2>
              <span className="text-xs text-gray-400 bg-gray-100 px-2.5 py-1 rounded-full">🔒 Locked</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 relative">
              {previewProtocols.map((p, idx) => (
                <div key={p.id || idx} className="bg-white border border-gray-200 rounded-lg p-4 relative overflow-hidden" data-testid={`protocol-preview-${idx}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-bold text-xs">{idx + 1}</div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-purple-600">Protocol</span>
                  </div>
                  <h3 className="text-sm font-bold text-gray-900 mb-1 select-none filter blur-sm">{p.name}</h3>
                  <p className="text-xs text-gray-500 line-clamp-2 select-none filter blur-sm">{p.goal || p.best_for}</p>
                  <div className="mt-2 flex items-center gap-1 text-xs">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span className="text-gray-400 filter blur-sm">{p.duration || '4 weeks'}</span>
                  </div>
                </div>
              ))}
              {totalProtocols > 6 && (
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 border-2 border-dashed border-purple-200 rounded-lg p-4 flex items-center justify-center">
                  <p className="text-center text-purple-600 font-semibold text-sm">+ {totalProtocols - 6} more protocols</p>
                </div>
              )}
            </div>
          </div>

          {/* CTA section */}
          <div className="bg-gradient-to-br from-purple-600 to-blue-700 rounded-2xl p-8 text-center shadow-xl">
            <h3 className="text-2xl font-bold text-white mb-2">Unlock Lifetime Access</h3>
            <p className="text-purple-100 text-sm mb-1">Get all <strong>13 Stack Hubs</strong> and <strong>130+ Premium Protocols</strong></p>
            <p className="text-purple-200 text-xs mb-6">One-time payment · Future updates included forever</p>

            <div className="flex items-baseline justify-center gap-2 mb-6">
              <span className="text-5xl font-bold text-white">$39.99</span>
              <span className="text-purple-200 text-sm">USDT</span>
            </div>

            <Link
              to={user ? '/checkout?product=lifetime' : '/login?redirect=/stacks/' + (hub.slug || '')}
              className="inline-block bg-white hover:bg-purple-50 text-purple-700 font-bold px-8 py-3 rounded-xl transition-all shadow-lg hover:shadow-xl"
              data-testid="hub-paywall-cta"
            >
              {user ? 'Unlock Now' : 'Sign In & Unlock'}
            </Link>

            <p className="text-purple-200 text-[11px] mt-4">
              {user ? 'Pay with USDT-TRC20 · Instant access' : 'No account? Sign up free, then unlock'}
            </p>

            {/* Trust signals */}
            <div className="mt-6 pt-6 border-t border-white/20 grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-white font-bold text-lg">130+</div>
                <div className="text-purple-200 text-[10px] uppercase tracking-wider">Protocols</div>
              </div>
              <div>
                <div className="text-white font-bold text-lg">13</div>
                <div className="text-purple-200 text-[10px] uppercase tracking-wider">Stack Hubs</div>
              </div>
              <div>
                <div className="text-white font-bold text-lg">∞</div>
                <div className="text-purple-200 text-[10px] uppercase tracking-wider">Updates</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  var protocolsList = hub.protocols || [];
  var coreInfo = hub.core_info || {};
  var pairings = coreInfo.common_pairings || [];
  var akaList = hub.also_known_as || [];
  var heroImg = API + '/api/hubs/hero-image/' + (hub.peptide_slug || hub.slug || '');
  var hasAnyRatings = protocolsList.some(p => (p.rating_count || 0) > 0);
  var avgRatingAll = (() => {
    var rated = protocolsList.filter(p => (p.rating_count || 0) > 0);
    if (!rated.length) return 0;
    var sum = rated.reduce((a, p) => a + (p.rating_avg || 0) * (p.rating_count || 0), 0);
    var n = rated.reduce((a, p) => a + (p.rating_count || 0), 0);
    return n > 0 ? Math.round((sum / n) * 10) / 10 : 0;
  })();

  return (
    <div className="min-h-screen bg-gray-50" data-testid="hub-detail-page">
      {/* Hero — immersive with background image */}
      <div className="relative bg-[#0f1729]">
        <div className="h-28 sm:h-36 lg:h-44 relative overflow-hidden">
          <img src={heroImg} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0f1729] via-[#0f1729]/70 to-[#0f1729]/20" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0f1729]/40 via-transparent to-transparent" />
        </div>

        <div className="relative px-4 sm:px-6 pb-7 pt-4 max-w-6xl mx-auto">
          <button onClick={() => navigate('/protocols')} className="inline-flex items-center gap-1.5 text-gray-300 hover:text-white text-sm mb-3 transition-colors" data-testid="back-to-library">
            <ChevronLeft className="w-4 h-4" />
            Back to Library
          </button>

          <div className="flex flex-wrap items-center gap-2 mb-3">
            {hub.category && (
              <span className="bg-white/15 border border-white/25 text-white text-xs font-medium px-2.5 py-1 rounded-full backdrop-blur">{hub.category}</span>
            )}
            {hub.classification && (
              <span className="bg-white/10 border border-white/20 text-gray-200 text-xs px-2.5 py-1 rounded-full backdrop-blur">{hub.classification}</span>
            )}
            <span className="inline-flex items-center gap-1 bg-yellow-500/20 border border-yellow-300/40 text-yellow-200 text-xs font-semibold px-2.5 py-1 rounded-full backdrop-blur">
              <Sparkles className="w-3 h-3" />
              PREMIUM
            </span>
            <span className="bg-purple-500/30 text-purple-100 border border-purple-300/40 text-xs font-semibold px-2.5 py-1 rounded-full backdrop-blur">{protocolsList.length} Protocols</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-bold mb-2 text-white" data-testid="hub-title">
            {hub.peptide_name}
          </h1>
          <p className="text-xs sm:text-sm text-purple-300 mb-3 uppercase tracking-[0.18em] font-semibold">{hub.subtitle || 'Premium Protocol Collection'}</p>
          <p className="text-sm sm:text-base text-gray-300 mb-3 max-w-3xl leading-relaxed">{hub.description}</p>

          {akaList.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 mt-3">
              <span className="text-xs text-gray-400">Also known as:</span>
              {akaList.map(function(aka, i) {
                return <span key={i} className="text-xs text-gray-300 bg-white/10 px-2.5 py-1 rounded-full">{aka}</span>;
              })}
            </div>
          )}

          {/* Stats strip */}
          <div className="mt-5 flex flex-wrap gap-x-7 gap-y-3 text-sm pt-4 border-t border-white/10">
            <Stat label="Protocols" value={protocolsList.length} />
            {coreInfo.common_cycle && <Stat label="Cycle Length" value={coreInfo.common_cycle} />}
            {avgRatingAll > 0 && <Stat label="Avg Rating" value={`${avgRatingAll} \u2605`} />}
          </div>
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
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            {protocolsList.length} Protocol Variations
          </h2>
          {hasAnyRatings && (
            <div className="inline-flex items-center bg-white border border-gray-200 rounded-lg p-1 shadow-sm" data-testid="sort-toggle">
              <button
                onClick={() => setSortMode('default')}
                className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-md transition-all ${sortMode === 'default' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:text-gray-900'}`}
                data-testid="sort-default-btn"
              >
                <List className="w-3.5 h-3.5" />
                Default
              </button>
              <button
                onClick={() => setSortMode('trending')}
                className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-md transition-all ${sortMode === 'trending' ? 'bg-orange-600 text-white' : 'text-gray-600 hover:text-gray-900'}`}
                data-testid="sort-trending-btn"
              >
                <Flame className="w-3.5 h-3.5" />
                Trending
              </button>
              <button
                onClick={() => setSortMode('top')}
                className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-md transition-all ${sortMode === 'top' ? 'bg-yellow-500 text-white' : 'text-gray-600 hover:text-gray-900'}`}
                data-testid="sort-top-btn"
              >
                <Star className="w-3.5 h-3.5" />
                Top Rated
              </button>
            </div>
          )}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="protocols-grid">
          {sortedProtocols.map(function(p, idx) {
            var compounds = p.compounds || [];
            var isTrending = trendingTopIds.has(p.id);
            return (
              <div
                key={p.id}
                onClick={() => setSelectedProtocol(p)}
                className={`bg-white border rounded-xl p-5 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-lg relative overflow-hidden flex flex-col ${isTrending ? 'border-orange-300 hover:shadow-orange-100/60 hover:border-orange-400' : 'border-gray-200 hover:shadow-purple-100/60 hover:border-purple-200'}`}
                data-testid={`protocol-card-${p.id}`}
              >
                {isTrending && (
                  <div className="absolute top-0 right-0 z-10">
                    <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-bl-lg flex items-center gap-1 shadow-md" data-testid={`trending-badge-${p.id}`}>
                      <Flame className="w-3 h-3" />
                      Trending
                    </div>
                  </div>
                )}
                <div className={`absolute top-0 right-0 w-20 h-20 rounded-bl-full ${isTrending ? 'bg-gradient-to-bl from-orange-50 to-transparent' : 'bg-gradient-to-bl from-purple-50 to-transparent'}`} />
                <div className="flex items-start justify-between mb-3 relative">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${isTrending ? 'bg-orange-100 text-orange-700' : 'bg-purple-100 text-purple-700'}`}>{idx + 1}</div>
                  {!isTrending && (
                    <span className="bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full">Protocol</span>
                  )}
                </div>
                <h3 className="text-base font-bold text-gray-900 mb-1 leading-snug">{p.name}</h3>
                <p className="text-gray-500 text-sm mb-3 line-clamp-2 flex-1">{p.goal}</p>

                {/* Duration pill */}
                {p.duration && (
                  <div className="inline-flex items-center gap-1 text-[11px] text-purple-700 bg-purple-50 border border-purple-100 px-2 py-0.5 rounded-md font-medium mb-3 w-fit">
                    <Clock className="w-3 h-3" />
                    {p.duration}
                  </div>
                )}

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
          index={sortedProtocols.findIndex(x => x.id === selectedProtocol.id) + 1}
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
                var uiInfo = calculateUI(c.name, c.dose);
                return (
                  <li key={i} className="text-sm bg-gray-50 px-3 py-2 rounded-lg">
                    <div className="flex items-start gap-2.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                      <div className="flex-1 flex flex-wrap justify-between gap-2">
                        <span className="font-semibold text-gray-900">{c.name}</span>
                        <span className="text-gray-600 font-medium">{c.dose}</span>
                      </div>
                    </div>
                    {uiInfo && (
                      <div className="mt-1 ml-4 flex items-center gap-1.5 text-[11px] text-blue-700">
                        <Syringe className="w-3 h-3" />
                        <span>
                          <strong>{uiInfo.ui} UI</strong> on insulin syringe
                          <span className="text-gray-500"> · {uiInfo.vialMg}mg vial in {uiInfo.diluentMl}ml water</span>
                        </span>
                      </div>
                    )}
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

          {protocol.duration && (
            <ProtocolSection icon={<Clock className="w-4 h-4" />} title="Duration">
              <p className="text-gray-700 text-sm">{protocol.duration}</p>
            </ProtocolSection>
          )}

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

function Stat({ label, value }) {
  return (
    <div>
      <p className="text-2xl font-bold text-white leading-none">{value}</p>
      <p className="text-[11px] text-purple-200 uppercase tracking-wider font-medium mt-1">{label}</p>
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

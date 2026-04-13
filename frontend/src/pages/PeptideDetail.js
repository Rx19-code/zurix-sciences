import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeft, Beaker, FlaskConical, BookOpen, GitCompare, Info, Clock, Award, RefreshCw, Tag, Layers, Lock } from 'lucide-react';

var API = process.env.REACT_APP_BACKEND_URL;

export default function PeptideDetail() {
  var params = useParams();
  var slug = params.slug;
  var navigate = useNavigate();
  var [peptide, setPeptide] = useState(null);
  var [tab, setTab] = useState('overview');
  var [loading, setLoading] = useState(true);

  useEffect(function() {
    fetch(API + '/api/library/' + slug)
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.error) { navigate('/protocols'); return; }
        setPeptide(data);
        setLoading(false);
      })
      .catch(function() { navigate('/protocols'); });
  }, [slug, navigate]);

  if (loading || !peptide) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  var akaList = peptide.also_known_as || [];
  var presList = peptide.presentations || [];

  var catSlug = (peptide.category || '').toLowerCase().replace(/ \/ /g, '-').replace(/ /g, '-');
  var heroImg = API + '/api/library/category-image/' + catSlug;

  return (
    <div className="min-h-screen bg-gray-50" data-testid="peptide-detail-page">
      {/* Header with Hero Image */}
      <div className="relative bg-[#0f1729]">
        {/* Hero Image */}
        <div className="h-40 sm:h-56 lg:h-64 relative overflow-hidden">
          <img src={heroImg} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0f1729] via-[#0f1729]/60 to-transparent" />
        </div>
        {/* Content below hero - always on dark background */}
        <div className="relative px-4 sm:px-6 pb-6 pt-4 max-w-5xl mx-auto">
          <button data-testid="back-to-library" onClick={function() { navigate('/protocols'); }} className="inline-flex items-center gap-1.5 text-gray-300 hover:text-white text-sm mb-3 transition-colors">
            <ChevronLeft className="w-4 h-4" />
            Back to Protocols
          </button>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="bg-white/15 border border-white/25 text-white text-xs font-medium px-2.5 py-1 rounded-full">{peptide.category}</span>
            {peptide.classification && (
              <span className="bg-white/10 border border-white/20 text-gray-200 text-xs px-2.5 py-1 rounded-full">{peptide.classification}</span>
            )}
            {peptide.evidence_level && (
              <span className="bg-green-500/20 text-green-300 border border-green-400/30 text-xs font-semibold px-2.5 py-1 rounded-full">{peptide.evidence_level}</span>
            )}
            <span className={peptide.is_free ? 'bg-green-500/20 text-green-300 border border-green-400/30 text-xs font-semibold px-2.5 py-1 rounded-full' : 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/30 text-xs font-semibold px-2.5 py-1 rounded-full'}>
              {peptide.is_free ? 'FREE' : 'PRO'}
            </span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-bold mb-2 text-white" data-testid="peptide-name">{peptide.name}</h1>
          <p className="text-sm sm:text-lg text-gray-300 mb-3">{peptide.description}</p>
          {akaList.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-gray-400 pt-1">Also known as:</span>
              {akaList.map(function(aka, i) {
                return <span key={i} className="text-xs text-gray-300 bg-white/10 px-2.5 py-1 rounded-full">{aka}</span>;
              })}
            </div>
          )}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        {/* Tabs */}
        <div className="flex border-b border-gray-200 bg-white rounded-t-lg -mt-px overflow-x-auto">
          <TabBtn active={tab === 'overview'} onClick={function() { setTab('overview'); }} icon={<Info className="w-4 h-4" />} label="Overview" tid="tab-overview" />
          <TabBtn active={tab === 'protocols'} onClick={function() { setTab('protocols'); }} icon={<Beaker className="w-4 h-4" />} label="Protocols" tid="tab-protocols" />
          <TabBtn active={tab === 'research'} onClick={function() { setTab('research'); }} icon={<BookOpen className="w-4 h-4" />} label="Research" tid="tab-research" />
          <TabBtn active={tab === 'synergy'} onClick={function() { setTab('synergy'); }} icon={<GitCompare className="w-4 h-4" />} label="Synergy" tid="tab-synergy" />
        </div>

        {/* Content */}
        <div className="py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-5">
            {tab === 'overview' && <OverviewContent peptide={peptide} />}
            {tab === 'protocols' && (!peptide.is_free ? <LockedContent /> : <ProtocolsContent peptide={peptide} />)}
            {tab === 'research' && (!peptide.is_free ? <LockedContent /> : <ResearchContent peptide={peptide} />)}
            {tab === 'synergy' && (!peptide.is_free ? <LockedContent /> : <SynergyContent peptide={peptide} />)}
          </div>
          <div className="lg:col-span-1">
            <QuickFacts peptide={peptide} />
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Tab Button ── */
function TabBtn({ active, onClick, icon, label, tid }) {
  return (
    <button data-testid={tid} onClick={onClick}
      className={'flex items-center gap-2 px-4 sm:px-5 py-3.5 text-sm font-medium whitespace-nowrap transition-colors border-b-2 ' + (active ? 'text-blue-600 border-blue-500 bg-blue-50/50' : 'text-gray-500 border-transparent hover:text-gray-700')}>
      {icon}
      {label}
    </button>
  );
}

/* ── Locked Content ── */
function LockedContent() {
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden" data-testid="locked-content">
      <div className="px-6 py-12 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Lock className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-bold text-gray-900 mb-2">Premium Content</h3>
        <p className="text-gray-500 text-sm mb-6 max-w-md mx-auto">
          This content requires a lifetime access subscription. Get full access to all protocols, research data, and synergy information.
        </p>
        <div className="inline-flex items-center gap-2 bg-yellow-500 text-white font-semibold px-6 py-3 rounded-lg">
          <Lock className="w-4 h-4" />
          Unlock Full Access
        </div>
        <p className="text-xs text-gray-400 mt-3">One-time payment via USDT</p>
      </div>
    </div>
  );
}

/* ── Card ── */
function Card({ icon, title, children }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <div className="flex items-center gap-2.5 px-5 py-4 border-b border-gray-100">
        {icon && <span className="text-blue-600">{icon}</span>}
        <h2 className="text-base font-bold text-gray-900">{title}</h2>
      </div>
      <div className="px-5 py-4">{children}</div>
    </div>
  );
}

/* ══════════════════ OVERVIEW ══════════════════ */
function OverviewContent({ peptide }) {
  var ov = peptide.overview;
  if (!ov) return <EmptyState text="Overview data coming soon." />;
  return (
    <>
      {ov.what_is && (
        <Card icon={<FlaskConical className="w-5 h-5" />} title={'What is ' + peptide.name}>
          <p className="text-gray-600 leading-relaxed">{ov.what_is}</p>
        </Card>
      )}
      {ov.mechanism_summary && (
        <Card icon={<Info className="w-5 h-5" />} title="Mechanism Summary">
          <p className="text-gray-600 leading-relaxed">{ov.mechanism_summary}</p>
        </Card>
      )}
    </>
  );
}

/* ══════════════════ PROTOCOLS ══════════════════ */
function ProtocolsContent({ peptide }) {
  var pr = peptide.protocols;
  if (!pr) return <EmptyState text="Protocol data coming soon." />;
  var dosageList = pr.dosages || [];
  var phaseList = pr.phases || [];
  var reconSteps = pr.reconstitution_steps || [];
  return (
    <>
      {/* Protocol Header */}
      {pr.title && (
        <Card icon={<Beaker className="w-5 h-5" />} title={pr.title}>
          {pr.standard && (
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                <div className="text-xs text-blue-500 font-medium mb-0.5">Route</div>
                <div className="text-gray-900 font-semibold text-sm">{pr.standard.route}</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                <div className="text-xs text-blue-500 font-medium mb-0.5">Frequency</div>
                <div className="text-gray-900 font-semibold text-sm">{pr.standard.frequency}</div>
              </div>
            </div>
          )}

          {/* Dosage by Indication */}
          {dosageList.length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-gray-800 mb-3">Dosage by Indication</h3>
              <div className="overflow-x-auto border border-gray-200 rounded-lg">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="text-left py-2.5 px-3 text-gray-500 font-medium text-xs uppercase">Indication</th>
                      <th className="text-left py-2.5 px-3 text-gray-500 font-medium text-xs uppercase">Dose</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dosageList.map(function(d, i) {
                      return (
                        <tr key={i} className="border-t border-gray-100">
                          <td className="py-3 px-3">
                            <div className="text-gray-900 font-medium">{d.indication}</div>
                            {d.schedule && <div className="text-xs text-gray-400 mt-0.5">{d.schedule}</div>}
                          </td>
                          <td className="py-3 px-3">
                            <span className="text-green-600 font-bold">{d.dose}</span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Protocol Phases */}
      {phaseList.length > 0 && (
        <Card icon={<Layers className="w-5 h-5" />} title="Protocol Phases">
          <div className="overflow-x-auto border border-gray-200 rounded-lg">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left py-2.5 px-3 text-gray-500 font-medium text-xs uppercase w-10">#</th>
                  <th className="text-left py-2.5 px-3 text-gray-500 font-medium text-xs uppercase">Phase</th>
                  <th className="text-left py-2.5 px-3 text-gray-500 font-medium text-xs uppercase">Dose</th>
                </tr>
              </thead>
              <tbody>
                {phaseList.map(function(p, i) {
                  return (
                    <tr key={i} className="border-t border-gray-100">
                      <td className="py-3 px-3">
                        <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center">{p.number}</span>
                      </td>
                      <td className="py-3 px-3 text-gray-900 font-medium">{p.phase}</td>
                      <td className="py-3 px-3"><span className="text-green-600 font-bold">{p.dose}</span></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Reconstitution */}
      {reconSteps.length > 0 && (
        <Card icon={<RefreshCw className="w-5 h-5" />} title="Reconstitution">
          <div className="flex items-center justify-between mb-4">
            <p className="text-gray-500 text-sm">{pr.reconstitution || ''}</p>
            <Link to="/calculator" data-testid="calc-dose-btn" className="inline-flex items-center gap-1.5 bg-blue-600 text-white text-xs font-semibold px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors shrink-0 ml-3">
              <Beaker className="w-3.5 h-3.5" />
              Calculate Dose
            </Link>
          </div>
          <div className="space-y-3">
            {reconSteps.map(function(step, i) {
              return (
                <div key={i} className="flex gap-3 items-start">
                  <span className="w-7 h-7 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">{i + 1}</span>
                  <p className="text-gray-600 text-sm pt-1">{step}</p>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Fallback for old structure without title */}
      {!pr.title && pr.standard && (
        <Card icon={<Beaker className="w-5 h-5" />} title="Standard Protocol">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="text-xs text-blue-500 font-medium mb-0.5">Route</div>
              <div className="text-gray-900 font-semibold text-sm">{pr.standard.route}</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="text-xs text-blue-500 font-medium mb-0.5">Frequency</div>
              <div className="text-gray-900 font-semibold text-sm">{pr.standard.frequency}</div>
            </div>
          </div>
          {pr.reconstitution && <p className="text-gray-500 text-sm mt-3">{pr.reconstitution}</p>}
        </Card>
      )}
    </>
  );
}

/* ══════════════════ RESEARCH ══════════════════ */
function ResearchContent({ peptide }) {
  var rs = peptide.research;
  if (!rs) return <EmptyState text="Research data coming soon." />;
  var stepsList = rs.steps || [];
  var refsList = rs.references || [];
  return (
    <>
      {rs.mechanism && (
        <Card icon={<BookOpen className="w-5 h-5" />} title="Mechanism of Action">
          <p className="text-gray-600 leading-relaxed mb-4">{rs.mechanism}</p>
          {stepsList.length > 0 && (
            <div className="space-y-2.5 mt-4 pt-4 border-t border-gray-100">
              {stepsList.map(function(step, i) {
                return (
                  <div key={i} className="flex gap-3 items-start">
                    <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">{i + 1}</span>
                    <p className="text-gray-700 text-sm pt-0.5">{step}</p>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      )}

      {refsList.length > 0 && (
        <Card icon={<BookOpen className="w-5 h-5" />} title="Scientific References">
          <div className="space-y-4">
            {refsList.map(function(ref, i) {
              var metaTags = ref.metadata || [];
              return (
                <div key={i} className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                  <h4 className="text-gray-900 font-semibold text-sm mb-2">{ref.title || ref}</h4>
                  {metaTags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {metaTags.map(function(tag, j) {
                        return <span key={j} className="text-xs bg-blue-50 text-blue-600 border border-blue-200 px-2 py-0.5 rounded-full">{tag}</span>;
                      })}
                    </div>
                  )}
                  {ref.summary && <p className="text-gray-500 text-sm italic">{ref.summary}</p>}
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </>
  );
}

/* ══════════════════ SYNERGY ══════════════════ */
function SynergyContent({ peptide }) {
  var sy = peptide.synergy;
  if (!sy) return <EmptyState text="Synergy data coming soon." />;
  var interList = sy.interactions || [];
  var stackList = sy.stacks || [];
  if (interList.length === 0 && stackList.length === 0) {
    return <EmptyState text="Synergy data coming soon for this peptide." />;
  }
  return (
    <>
      {interList.length > 0 && (
        <Card icon={<GitCompare className="w-5 h-5" />} title="Interactions with Other Peptides">
          {/* Summary Table */}
          <div className="overflow-x-auto border border-gray-200 rounded-lg mb-5">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left py-2.5 px-3 text-gray-500 font-medium text-xs uppercase">Peptide</th>
                  <th className="text-right py-2.5 px-3 text-gray-500 font-medium text-xs uppercase">Status</th>
                </tr>
              </thead>
              <tbody>
                {interList.map(function(item, i) {
                  return (
                    <tr key={i} className="border-t border-gray-100">
                      <td className="py-2.5 px-3 text-gray-900 font-medium">{item.peptide}</td>
                      <td className="py-2.5 px-3 text-right"><StatusBadge status={item.status} /></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {/* Detail Cards */}
          <div className="space-y-3">
            {interList.map(function(item, i) {
              var borderColor = item.status === 'SYNERGISTIC' ? 'border-l-green-500 bg-green-50/50' : item.status === 'MONITOR' ? 'border-l-amber-500 bg-amber-50/50' : 'border-l-cyan-500 bg-cyan-50/50';
              return (
                <div key={i} className={'rounded-lg p-4 border border-gray-100 border-l-[3px] ' + borderColor}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-gray-900 font-semibold">{item.peptide}</span>
                    <StatusBadge status={item.status} />
                  </div>
                  <p className="text-gray-500 text-sm">{item.description}</p>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {stackList.length > 0 && (
        <Card icon={<Layers className="w-5 h-5" />} title="Recommended Stacks">
          <div className="space-y-4">
            {stackList.map(function(stack, i) {
              var pepNames = stack.peptides || [];
              return (
                <div key={i} className="bg-gray-50 rounded-xl p-5 border border-gray-200">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                    <h4 className="text-gray-900 font-bold">{stack.name}</h4>
                    {stack.goal && (
                      <span className="text-xs bg-amber-100 text-amber-700 border border-amber-200 px-2.5 py-1 rounded-full font-medium">{stack.goal}</span>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {pepNames.map(function(pName, j) {
                      return <span key={j} className="text-xs bg-green-100 text-green-700 border border-green-200 px-2.5 py-1 rounded-full font-semibold">{pName}</span>;
                    })}
                  </div>
                  <p className="text-gray-600 text-sm leading-relaxed">{stack.description}</p>
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </>
  );
}

/* ── Quick Facts Sidebar ── */
function QuickFacts({ peptide }) {
  var akaList = peptide.also_known_as || [];
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm sticky top-6">
      <div className="px-5 py-4 border-b border-gray-100">
        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Quick Facts</h3>
      </div>
      <div className="px-5 py-4 space-y-5">
        {peptide.classification && (
          <FactItem icon={<FlaskConical className="w-4 h-4" />} label="Classification" value={peptide.classification} />
        )}
        {peptide.evidence_level && (
          <FactItem icon={<Award className="w-4 h-4" />} label="Evidence Level">
            <span className="inline-block text-xs font-semibold bg-green-100 text-green-700 border border-green-200 px-2.5 py-1 rounded-full">{peptide.evidence_level}</span>
          </FactItem>
        )}
        {peptide.half_life && (
          <FactItem icon={<Clock className="w-4 h-4" />} label="Half-life" value={peptide.half_life} />
        )}
        {peptide.reconstitution_difficulty && (
          <FactItem icon={<RefreshCw className="w-4 h-4" />} label="Reconstitution">
            <span className={'text-sm font-semibold ' + (peptide.reconstitution_difficulty === 'Easy' ? 'text-green-600' : peptide.reconstitution_difficulty === 'Hard' ? 'text-red-600' : 'text-amber-600')}>
              {peptide.reconstitution_difficulty}
            </span>
          </FactItem>
        )}
        {akaList.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Tag className="w-4 h-4 text-gray-400" />
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Alternative Names</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {akaList.map(function(aka, i) {
                return <span key={i} className="text-xs bg-gray-100 text-gray-600 border border-gray-200 px-2.5 py-1 rounded-full">{aka}</span>;
              })}
            </div>
          </div>
        )}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Beaker className="w-4 h-4 text-gray-400" />
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Category</span>
          </div>
          <span className="inline-block text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full">{peptide.category}</span>
        </div>
      </div>
    </div>
  );
}

function FactItem({ icon, label, value, children }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-gray-400">{icon}</span>
        <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">{label}</span>
      </div>
      {children || <span className="text-sm text-gray-900 font-medium">{value}</span>}
    </div>
  );
}

function StatusBadge({ status }) {
  var cls = 'text-xs font-bold px-2.5 py-1 rounded-full ';
  if (status === 'SYNERGISTIC') cls += 'bg-green-100 text-green-700';
  else if (status === 'COMPATIBLE') cls += 'bg-cyan-100 text-cyan-700';
  else if (status === 'MONITOR') cls += 'bg-amber-100 text-amber-700';
  else if (status === 'AVOID') cls += 'bg-red-100 text-red-700';
  else cls += 'bg-gray-100 text-gray-700';
  return <span className={cls}>{status}</span>;
}

function EmptyState({ text }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-12 text-center text-gray-400">
      <p>{text}</p>
    </div>
  );
}

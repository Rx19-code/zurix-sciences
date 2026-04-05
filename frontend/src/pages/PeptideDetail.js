import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

export default function PeptideDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [peptide, setPeptide] = useState(null);
  const [tab, setTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(API + '/api/library/' + slug)
      .then(r => r.json())
      .then(data => {
        if (data.error) { navigate('/library'); return; }
        setPeptide(data);
        setLoading(false);
      })
      .catch(() => navigate('/library'));
  }, [slug, navigate]);

  if (loading || !peptide) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  var akaList = peptide.also_known_as || [];
  var presList = peptide.presentations || [];
  var presText = presList.join(' | ');

  return (
    <div className="min-h-screen bg-gray-50" data-testid="peptide-detail-page">
      {/* Hero header */}
      <div className="bg-gradient-to-b from-blue-600 to-blue-800 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-6 pb-8">
          <button data-testid="back-to-library" onClick={() => navigate('/library')} className="inline-flex items-center gap-2 text-blue-100 hover:text-white text-sm mb-5 transition-colors">
            &larr; Back to Library
          </button>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="bg-white/15 border border-white/20 text-white text-xs font-medium px-2.5 py-1 rounded-full">{peptide.category}</span>
            <span className={peptide.is_free ? 'bg-green-500/20 text-green-200 border border-green-400/30 text-xs font-semibold px-2.5 py-1 rounded-full' : 'bg-yellow-500/20 text-yellow-200 border border-yellow-400/30 text-xs font-semibold px-2.5 py-1 rounded-full'}>
              {peptide.is_free ? 'FREE' : 'PRO'}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold mb-2" data-testid="peptide-name">{peptide.name}</h1>
          <p className="text-lg text-blue-100 mb-3">{peptide.description}</p>
          {akaList.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {akaList.map((aka, i) => (
                <span key={i} className="text-xs text-blue-200 bg-white/10 px-2.5 py-1 rounded-full">{aka}</span>
              ))}
            </div>
          )}
          {presList.length > 0 && (
            <div className="text-sm text-blue-200 mt-2">Presentations: {presText}</div>
          )}
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <TabBar tab={tab} setTab={setTab} />

        <div className="space-y-6 pb-10">
          {tab === 'overview' && <OverviewTab data={peptide.overview} />}
          {tab === 'protocols' && <ProtocolsTab data={peptide.protocols} />}
          {tab === 'research' && <ResearchTab data={peptide.research} />}
          {tab === 'synergy' && <SynergyTab data={peptide.synergy} />}
        </div>
      </div>
    </div>
  );
}

function TabBar({ tab, setTab }) {
  var tabs = ['overview', 'protocols', 'research', 'synergy'];
  var labels = { overview: 'Overview', protocols: 'Protocols', research: 'Research', synergy: 'Synergy' };
  return (
    <div className="flex border-b border-gray-200 mb-8 overflow-x-auto bg-white rounded-t-lg mt-[-1px]">
      {tabs.map(t => (
        <button key={t} data-testid={'tab-' + t} onClick={() => setTab(t)}
          className={'px-4 sm:px-6 py-3 text-sm font-medium whitespace-nowrap transition-colors ' + (tab === t ? 'text-blue-600 border-b-2 border-blue-500 bg-blue-50/50' : 'text-gray-500 border-b-2 border-transparent hover:text-gray-700')}>
          {labels[t]}
        </button>
      ))}
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 sm:p-6 mb-4 shadow-sm">
      <h2 className="text-lg font-bold text-gray-900 mb-4">{title}</h2>
      {children}
    </div>
  );
}

function OverviewTab({ data }) {
  if (!data) return <EmptyMsg text="Overview data coming soon." />;
  return (
    <div>
      {data.what_is && (
        <Card title="What is it">
          <p className="text-gray-600 leading-relaxed">{data.what_is}</p>
        </Card>
      )}
      {data.mechanism_summary && (
        <Card title="Mechanism Summary">
          <p className="text-gray-600 leading-relaxed">{data.mechanism_summary}</p>
        </Card>
      )}
    </div>
  );
}

function ProtocolsTab({ data }) {
  if (!data) return <EmptyMsg text="Protocol data coming soon." />;
  var dosageList = data.dosages || [];
  return (
    <div>
      {data.standard && (
        <Card title="Standard Protocol">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
              <div className="text-xs text-gray-500 mb-1">Route</div>
              <div className="text-gray-900 font-medium text-sm">{data.standard.route}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
              <div className="text-xs text-gray-500 mb-1">Frequency</div>
              <div className="text-gray-900 font-medium text-sm">{data.standard.frequency}</div>
            </div>
          </div>
          {data.reconstitution && <p className="text-gray-500 text-sm">{data.reconstitution}</p>}
        </Card>
      )}
      {dosageList.length > 0 && (
        <Card title="Dosage Table">
          <DosageTable rows={dosageList} />
        </Card>
      )}
    </div>
  );
}

function DosageTable({ rows }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-2.5 px-3 text-gray-500 font-medium">Indication</th>
            <th className="text-left py-2.5 px-3 text-gray-500 font-medium">Dose</th>
            <th className="text-left py-2.5 px-3 text-gray-500 font-medium">Route</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((d, i) => (
            <tr key={i} className="border-b border-gray-100">
              <td className="py-2.5 px-3 text-gray-600">{d.indication}</td>
              <td className="py-2.5 px-3 text-gray-900 font-medium">{d.dose}</td>
              <td className="py-2.5 px-3 text-gray-600">{d.route}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ResearchTab({ data }) {
  if (!data) return <EmptyMsg text="Research data coming soon." />;
  var stepsList = data.steps || [];
  var refsList = data.references || [];
  return (
    <div>
      {data.mechanism && (
        <Card title="Mechanism of Action">
          <p className="text-gray-600 leading-relaxed mb-4">{data.mechanism}</p>
          {stepsList.length > 0 && (
            <div className="space-y-3">
              {stepsList.map((step, i) => (
                <div key={i} className="flex gap-3">
                  <div className="w-7 h-7 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 text-xs font-bold shrink-0">
                    {i + 1}
                  </div>
                  <p className="text-gray-600 text-sm pt-1">{step}</p>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
      {refsList.length > 0 && (
        <Card title="Scientific References">
          <ul className="space-y-2">
            {refsList.map((ref, i) => (
              <li key={i} className="text-gray-500 text-sm pl-4 relative before:content-[''] before:absolute before:left-0 before:top-2 before:w-1.5 before:h-1.5 before:rounded-full before:bg-blue-500">
                {ref}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

function SynergyTab({ data }) {
  if (!data) return <EmptyMsg text="Synergy data coming soon." />;
  var interList = data.interactions || [];
  var stackList = data.stacks || [];
  if (interList.length === 0 && stackList.length === 0) {
    return <EmptyMsg text="Synergy data coming soon for this peptide." />;
  }
  return (
    <div>
      {interList.length > 0 && (
        <Card title="Interactions">
          <div className="space-y-3">
            {interList.map((item, i) => (
              <InteractionItem key={i} item={item} />
            ))}
          </div>
        </Card>
      )}
      {stackList.length > 0 && (
        <Card title="Recommended Stacks">
          <div className="space-y-3">
            {stackList.map((stack, i) => (
              <StackItem key={i} stack={stack} />
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

function InteractionItem({ item }) {
  var cls = 'rounded-lg p-4 ';
  var badge = '';
  if (item.status === 'SYNERGISTIC') {
    cls += 'bg-green-50 border-l-[3px] border-green-500';
    badge = 'text-green-600 bg-green-50';
  } else if (item.status === 'AVOID') {
    cls += 'bg-red-50 border-l-[3px] border-red-500';
    badge = 'text-red-600 bg-red-50';
  } else {
    cls += 'bg-blue-50 border-l-[3px] border-blue-500';
    badge = 'text-blue-600 bg-blue-50';
  }
  return (
    <div className={cls}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-gray-900 font-medium">{item.peptide}</span>
        <span className={'text-xs font-semibold px-2 py-0.5 rounded-full ' + badge}>{item.status}</span>
      </div>
      <p className="text-gray-500 text-sm">{item.description}</p>
    </div>
  );
}

function StackItem({ stack }) {
  var pepList = stack.peptides || [];
  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
      <h4 className="text-gray-900 font-medium mb-1">{stack.name}</h4>
      <div className="flex flex-wrap gap-1.5 mb-2">
        {pepList.map((pName, j) => (
          <span key={j} className="text-xs bg-blue-50 text-blue-600 border border-blue-200 px-2 py-0.5 rounded-full">{pName}</span>
        ))}
      </div>
      <p className="text-gray-500 text-sm">{stack.description}</p>
    </div>
  );
}

function EmptyMsg({ text }) {
  return (
    <div className="text-center py-12 text-gray-400">
      <p>{text}</p>
    </div>
  );
}

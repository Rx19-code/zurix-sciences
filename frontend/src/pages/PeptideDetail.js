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
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  var akaList = peptide.also_known_as || [];
  var presList = peptide.presentations || [];
  var presText = presList.join(' | ');

  return (
    <div className="min-h-screen bg-[#0a0e1a]" data-testid="peptide-detail-page">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <button data-testid="back-to-library" onClick={() => navigate('/library')} className="inline-flex items-center gap-2 text-gray-400 hover:text-white text-sm mb-6 transition-colors">
          Back to Library
        </button>

        <div className="bg-white/[0.03] border border-white/[0.06] rounded-2xl p-6 sm:p-8 mb-6">
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-medium px-2.5 py-1 rounded-full">{peptide.category}</span>
            <span className={peptide.is_free ? 'bg-green-500/10 text-green-400 border border-green-500/20 text-xs font-semibold px-2.5 py-1 rounded-full' : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 text-xs font-semibold px-2.5 py-1 rounded-full'}>
              {peptide.is_free ? 'FREE' : 'PRO'}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2" data-testid="peptide-name">{peptide.name}</h1>
          <p className="text-lg text-gray-400 mb-3">{peptide.description}</p>
          {akaList.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {akaList.map((aka, i) => (
                <span key={i} className="text-xs text-gray-500 bg-white/5 px-2.5 py-1 rounded-full">{aka}</span>
              ))}
            </div>
          )}
          {presList.length > 0 && (
            <div className="text-sm text-gray-500 mt-2">Presentations: {presText}</div>
          )}
        </div>

        <TabBar tab={tab} setTab={setTab} />

        <div className="space-y-6">
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
    <div className="flex border-b border-white/10 mb-8 overflow-x-auto">
      {tabs.map(t => (
        <button key={t} data-testid={'tab-' + t} onClick={() => setTab(t)}
          className={'px-4 sm:px-6 py-3 text-sm font-medium whitespace-nowrap transition-colors ' + (tab === t ? 'text-blue-400 border-b-2 border-blue-500 bg-blue-500/[0.08]' : 'text-gray-400 border-b-2 border-transparent hover:text-gray-200')}>
          {labels[t]}
        </button>
      ))}
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-5 sm:p-6 mb-4">
      <h2 className="text-lg font-bold text-white mb-4">{title}</h2>
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
          <p className="text-gray-300 leading-relaxed">{data.what_is}</p>
        </Card>
      )}
      {data.mechanism_summary && (
        <Card title="Mechanism Summary">
          <p className="text-gray-300 leading-relaxed">{data.mechanism_summary}</p>
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
            <div className="bg-white/[0.03] rounded-lg p-3">
              <div className="text-xs text-gray-500 mb-1">Route</div>
              <div className="text-white font-medium text-sm">{data.standard.route}</div>
            </div>
            <div className="bg-white/[0.03] rounded-lg p-3">
              <div className="text-xs text-gray-500 mb-1">Frequency</div>
              <div className="text-white font-medium text-sm">{data.standard.frequency}</div>
            </div>
          </div>
          {data.reconstitution && <p className="text-gray-400 text-sm">{data.reconstitution}</p>}
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
          <tr className="border-b border-white/10">
            <th className="text-left py-2.5 px-3 text-gray-400 font-medium">Indication</th>
            <th className="text-left py-2.5 px-3 text-gray-400 font-medium">Dose</th>
            <th className="text-left py-2.5 px-3 text-gray-400 font-medium">Route</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((d, i) => (
            <tr key={i} className="border-b border-white/5">
              <td className="py-2.5 px-3 text-gray-300">{d.indication}</td>
              <td className="py-2.5 px-3 text-white font-medium">{d.dose}</td>
              <td className="py-2.5 px-3 text-gray-300">{d.route}</td>
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
          <p className="text-gray-300 leading-relaxed mb-4">{data.mechanism}</p>
          {stepsList.length > 0 && (
            <div className="space-y-3">
              {stepsList.map((step, i) => (
                <div key={i} className="flex gap-3">
                  <div className="w-7 h-7 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 text-xs font-bold shrink-0">
                    {i + 1}
                  </div>
                  <p className="text-gray-300 text-sm pt-1">{step}</p>
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
              <li key={i} className="text-gray-400 text-sm pl-4 relative before:content-[''] before:absolute before:left-0 before:top-2 before:w-1.5 before:h-1.5 before:rounded-full before:bg-blue-400">
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
    cls += 'bg-green-500/[0.06] border-l-[3px] border-green-500';
    badge = 'text-green-400 bg-green-500/10';
  } else if (item.status === 'AVOID') {
    cls += 'bg-red-500/[0.06] border-l-[3px] border-red-500';
    badge = 'text-red-400 bg-red-500/10';
  } else {
    cls += 'bg-blue-500/[0.06] border-l-[3px] border-blue-500';
    badge = 'text-blue-400 bg-blue-500/10';
  }
  return (
    <div className={cls}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-white font-medium">{item.peptide}</span>
        <span className={'text-xs font-semibold px-2 py-0.5 rounded-full ' + badge}>{item.status}</span>
      </div>
      <p className="text-gray-400 text-sm">{item.description}</p>
    </div>
  );
}

function StackItem({ stack }) {
  var pepList = stack.peptides || [];
  return (
    <div className="bg-white/[0.03] rounded-lg p-4">
      <h4 className="text-white font-medium mb-1">{stack.name}</h4>
      <div className="flex flex-wrap gap-1.5 mb-2">
        {pepList.map((pName, j) => (
          <span key={j} className="text-xs bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-full">{pName}</span>
        ))}
      </div>
      <p className="text-gray-400 text-sm">{stack.description}</p>
    </div>
  );
}

function EmptyMsg({ text }) {
  return (
    <div className="text-center py-12 text-gray-500">
      <p>{text}</p>
    </div>
  );
}

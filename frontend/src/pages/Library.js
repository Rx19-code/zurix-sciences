import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_COLORS = {
  'Weight Loss / GLP-1': { bg: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-200' },
  'Nootropic / Cognitive': { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200' },
  'Aesthetics / Skin': { bg: 'bg-pink-50', text: 'text-pink-600', border: 'border-pink-200' },
  'Anti-aging': { bg: 'bg-cyan-50', text: 'text-cyan-600', border: 'border-cyan-200' },
  'Recovery': { bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-200' },
  'GH / Secretagogues': { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
  'Hormonal / Sexual Health': { bg: 'bg-rose-50', text: 'text-rose-600', border: 'border-rose-200' },
  'Immunity': { bg: 'bg-teal-50', text: 'text-teal-600', border: 'border-teal-200' },
  'Bioregulators': { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
  'Metabolism': { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200' },
  'Diluents': { bg: 'bg-gray-50', text: 'text-gray-600', border: 'border-gray-200' },
};

const getColor = (cat) => CATEGORY_COLORS[cat] || { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200' };

export default function Library() {
  const [peptides, setPeptides] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('peptides');
  const [stacks, setStacks] = useState([]);
  const [stackCategories, setStackCategories] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API}/api/library`)
      .then(r => r.json())
      .then(data => {
        setPeptides(data.peptides || []);
        setCategories(data.categories || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    fetch(`${API}/api/stacks`)
      .then(r => r.json())
      .then(data => {
        setStacks(data.stacks || []);
        setStackCategories(data.categories || []);
      })
      .catch(() => {});
  }, []);

  const filtered = useMemo(() => {
    let list = peptides;
    if (activeCategory !== 'All') {
      list = list.filter(p => p.category === activeCategory);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(p =>
        p.name.toLowerCase().includes(q) ||
        (p.description && p.description.toLowerCase().includes(q))
      );
    }
    return list;
  }, [peptides, activeCategory, search]);

  const freeCount = useMemo(() => peptides.filter(p => p.is_free).length, [peptides]);

  const filteredStacks = useMemo(() => {
    let list = stacks;
    if (activeCategory !== 'All') {
      list = list.filter(s => s.category === activeCategory);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(s =>
        s.name.toLowerCase().includes(q) ||
        s.goal.toLowerCase().includes(q) ||
        s.peptides.some(p => p.toLowerCase().includes(q))
      );
    }
    return list;
  }, [stacks, activeCategory, search]);

  const currentCategories = viewMode === 'peptides' ? categories : stackCategories;

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="library-page">
      {/* Hero */}
      <div className="bg-gradient-to-br from-blue-700 to-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
          <div className="text-center mb-6">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-3 text-white tracking-tight">
              Protocol Library
            </h1>
            <p className="text-base text-blue-100 max-w-2xl mx-auto">
              Complete protocols with dosages, scientific references, and synergies
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex justify-center mb-5">
            <div className="inline-flex bg-white/10 border border-white/20 rounded-xl p-1">
              <button
                data-testid="toggle-peptides"
                onClick={() => { setViewMode('peptides'); setActiveCategory('All'); }}
                className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all ${viewMode === 'peptides' ? 'bg-white text-blue-700 shadow-sm' : 'text-white hover:bg-white/10'}`}
              >
                Peptides ({peptides.length})
              </button>
              <button
                data-testid="toggle-stacks"
                onClick={() => { setViewMode('stacks'); setActiveCategory('All'); }}
                className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all ${viewMode === 'stacks' ? 'bg-white text-blue-700 shadow-sm' : 'text-white hover:bg-white/10'}`}
              >
                Stacks ({stacks.length})
              </button>
            </div>
          </div>

          <p className="text-center text-sm text-blue-200 mb-6">
            {viewMode === 'peptides'
              ? `${freeCount} of ${peptides.length} peptides accessible free`
              : `${stacks.length} stack protocols available`
            }
          </p>

          {/* Search */}
          <div className="max-w-xl mx-auto mb-6">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              data-testid="library-search"
              placeholder={viewMode === 'peptides' ? "Search peptide by name..." : "Search stack by name or peptide..."}
              className="w-full px-5 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-white/30 text-sm"
            />
          </div>

          {/* Categories */}
          <div className="flex flex-wrap justify-center gap-2">
            <button
              onClick={() => setActiveCategory('All')}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${activeCategory === 'All' ? 'bg-white text-blue-700' : 'bg-white/10 text-white hover:bg-white/20'}`}
            >
              All
            </button>
            {currentCategories.map(cat => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${activeCategory === cat ? 'bg-white text-blue-700' : 'bg-white/10 text-white hover:bg-white/20'}`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {viewMode === 'peptides' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4" data-testid="peptide-grid">
          {filtered.map(pep => {
            const color = getColor(pep.category);
            return (
              <div
                key={pep.slug}
                data-testid={`peptide-card-${pep.slug}`}
                onClick={() => navigate(`/protocols/${pep.slug}`)}
                className={`bg-white border border-gray-200 rounded-xl p-5 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-gray-200/60 ${!pep.is_free ? 'relative overflow-hidden' : ''}`}
              >
                {!pep.is_free && <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-bl from-yellow-100 to-transparent rounded-bl-full" />}
                <div className="flex items-center justify-between mb-3">
                  <span className={`${color.bg} ${color.text} border ${color.border} text-xs font-medium px-2 py-0.5 rounded-full`}>{pep.category}</span>
                  {pep.is_free ? (
                    <span className="bg-green-50 text-green-600 border border-green-200 text-xs font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" /></svg>
                      FREE
                    </span>
                  ) : (
                    <span className="bg-yellow-50 text-yellow-600 border border-yellow-200 text-xs font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" /></svg>
                      PRO
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-1">{pep.name}</h3>
                <p className="text-gray-500 text-sm mb-3 line-clamp-2">{pep.description}</p>
                <div className="text-xs text-gray-400">
                  {pep.presentations && pep.presentations.length > 0 && (
                    <span>Vial: {pep.presentations.join(', ')}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
        ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="stacks-grid">
          {filteredStacks.map(stack => {
            const pepList = stack.peptides || [];
            return (
              <div
                key={stack.slug}
                data-testid={`stack-card-${stack.slug}`}
                onClick={() => navigate(`/protocols/stack/${stack.slug}`)}
                className="bg-white border border-gray-200 rounded-xl p-5 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-gray-200/60 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-bl from-purple-100 to-transparent rounded-bl-full" />
                <div className="flex items-center justify-between mb-3">
                  <span className="bg-purple-50 text-purple-600 border border-purple-200 text-xs font-medium px-2 py-0.5 rounded-full">{stack.category}</span>
                  <span className="bg-yellow-50 text-yellow-600 border border-yellow-200 text-xs font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" /></svg>
                    PRO
                  </span>
                </div>
                <h3 className="text-base font-bold text-gray-900 mb-2">{stack.name}</h3>
                <p className="text-gray-500 text-sm mb-3 line-clamp-2">{stack.goal}</p>
                <div className="flex flex-wrap gap-1.5">
                  {pepList.map(function(p, i) {
                    return <span key={i} className="text-xs bg-blue-50 text-blue-600 border border-blue-200 px-2 py-0.5 rounded-full">{p}</span>;
                  })}
                </div>
              </div>
            );
          })}
        </div>
        )}
        {((viewMode === 'peptides' && filtered.length === 0) || (viewMode === 'stacks' && filteredStacks.length === 0)) && (
          <div className="text-center py-12 text-gray-500">
            <p>No {viewMode === 'peptides' ? 'peptides' : 'stacks'} found matching your criteria</p>
          </div>
        )}
      </div>
    </div>
  );
}

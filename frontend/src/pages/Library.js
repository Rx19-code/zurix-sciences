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
        (p.also_known_as || []).some(a => a.toLowerCase().includes(q))
      );
    }
    return list;
  }, [peptides, activeCategory, search]);

  const freeCount = useMemo(() => peptides.filter(p => p.is_free).length, [peptides]);

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
      <div className="relative overflow-hidden bg-gradient-to-b from-blue-600 to-blue-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-10 pb-6 relative">
          <div className="text-center mb-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/15 border border-white/20 text-white text-sm mb-4">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
              {peptides.length}+ Peptides Catalogued
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-3 text-white tracking-tight">
              Protocol Library
            </h1>
            <p className="text-base text-blue-100 max-w-2xl mx-auto">
              Complete protocols with dosages, scientific references, and synergies
            </p>
          </div>

          {/* Search */}
          <div className="max-w-xl mx-auto mb-6">
            <div className="relative">
              <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              <input
                data-testid="library-search"
                type="text"
                placeholder="Search peptide by name..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-white/15 border border-white/20 rounded-xl text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-white/40 transition-all"
              />
            </div>
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap justify-center gap-2 mb-3">
            <button
              data-testid="filter-all"
              onClick={() => setActiveCategory('All')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${activeCategory === 'All' ? 'bg-white text-blue-700' : 'bg-white/10 border border-white/20 text-white hover:bg-white/20'}`}
            >
              All
            </button>
            {categories.map(cat => (
              <button
                key={cat}
                data-testid={`filter-${cat.toLowerCase().replace(/[^a-z]/g, '-')}`}
                onClick={() => setActiveCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${activeCategory === cat ? 'bg-white text-blue-700' : 'bg-white/10 border border-white/20 text-white hover:bg-white/20'}`}
              >
                {cat}
              </button>
            ))}
          </div>
          <p className="text-center text-sm text-blue-200 mb-6">{freeCount} of {peptides.length} peptides accessible free</p>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4" data-testid="peptide-grid">
          {filtered.map(pep => {
            const color = getColor(pep.category);
            return (
              <div
                key={pep.slug}
                data-testid={`peptide-card-${pep.slug}`}
                onClick={() => navigate(`/library/${pep.slug}`)}
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
        {filtered.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <svg className="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            <p>No peptides found matching your criteria</p>
          </div>
        )}
      </div>

      {/* CTA Upgrade */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-600 rounded-2xl p-8 md:p-10 border border-blue-500/30 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-52 h-52 bg-gradient-to-bl from-white/5 to-transparent rounded-bl-full" />
          <div className="relative text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 border border-white/20 text-white text-sm font-medium mb-4">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" /></svg>
              Lifetime Access
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">
              Unlock All Protocols
            </h2>
            <p className="text-blue-100 max-w-2xl mx-auto mb-6">
              Full access to all advanced protocols, research data, synergies, and future updates. One-time payment.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-5">
              <button
                data-testid="pay-usdt-btn"
                className="bg-white px-6 py-3.5 rounded-xl text-blue-700 font-bold flex items-center gap-2 shadow-lg shadow-blue-900/30 hover:shadow-blue-900/40 transition-all hover:-translate-y-0.5"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <div className="text-left">
                  <div className="text-xs opacity-70">Cryptocurrency</div>
                  <div>Pay with USDT — $20.00</div>
                </div>
              </button>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-blue-100">
              <span className="flex items-center gap-1"><svg className="w-4 h-4 text-green-300" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" /></svg> {peptides.length}+ Protocols</span>
              <span className="flex items-center gap-1"><svg className="w-4 h-4 text-green-300" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" /></svg> Free Updates</span>
              <span className="flex items-center gap-1"><svg className="w-4 h-4 text-green-300" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" /></svg> Lifetime Access</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

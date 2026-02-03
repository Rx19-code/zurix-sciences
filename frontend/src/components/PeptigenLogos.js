import React from 'react';

// Logo Option 1: Molecular Triangle Style (inspired by design 1 & 8)
export const LogoMolecular = ({ className = "w-10 h-10" }) => (
  <svg className={className} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#10b981" />
        <stop offset="100%" stopColor="#3b82f6" />
      </linearGradient>
    </defs>
    
    {/* Outer molecular structure */}
    <circle cx="50" cy="20" r="3" fill="url(#gradient1)" />
    <circle cx="25" cy="75" r="3" fill="url(#gradient1)" />
    <circle cx="75" cy="75" r="3" fill="url(#gradient1)" />
    
    {/* Connecting lines */}
    <line x1="50" y1="20" x2="25" y2="75" stroke="url(#gradient1)" strokeWidth="1.5" opacity="0.6" />
    <line x1="50" y1="20" x2="75" y2="75" stroke="url(#gradient1)" strokeWidth="1.5" opacity="0.6" />
    <line x1="25" y1="75" x2="75" y2="75" stroke="url(#gradient1)" strokeWidth="1.5" opacity="0.6" />
    
    {/* Inner dots */}
    <circle cx="38" cy="48" r="2" fill="url(#gradient1)" />
    <circle cx="62" cy="48" r="2" fill="url(#gradient1)" />
    <circle cx="50" cy="65" r="2" fill="url(#gradient1)" />
    
    {/* P Letter */}
    <text x="50" y="58" fontSize="42" fontWeight="bold" fill="url(#gradient1)" textAnchor="middle" fontFamily="sans-serif">
      P
    </text>
  </svg>
);

// Logo Option 2: Network Style (inspired by design 2)
export const LogoNetwork = ({ className = "w-10 h-10" }) => (
  <svg className={className} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#8b5cf6" />
        <stop offset="50%" stopColor="#10b981" />
        <stop offset="100%" stopColor="#3b82f6" />
      </linearGradient>
    </defs>
    
    {/* Complex molecular network */}
    <circle cx="50" cy="30" r="3" fill="url(#gradient2)" />
    <circle cx="30" cy="50" r="3" fill="url(#gradient2)" />
    <circle cx="70" cy="50" r="3" fill="url(#gradient2)" />
    <circle cx="40" cy="70" r="3" fill="url(#gradient2)" />
    <circle cx="60" cy="70" r="3" fill="url(#gradient2)" />
    <circle cx="25" cy="35" r="2" fill="url(#gradient2)" opacity="0.7" />
    <circle cx="75" cy="35" r="2" fill="url(#gradient2)" opacity="0.7" />
    <circle cx="50" cy="80" r="2" fill="url(#gradient2)" opacity="0.7" />
    
    {/* Network connections */}
    <line x1="50" y1="30" x2="30" y2="50" stroke="url(#gradient2)" strokeWidth="1" opacity="0.4" />
    <line x1="50" y1="30" x2="70" y2="50" stroke="url(#gradient2)" strokeWidth="1" opacity="0.4" />
    <line x1="30" y1="50" x2="40" y2="70" stroke="url(#gradient2)" strokeWidth="1" opacity="0.4" />
    <line x1="70" y1="50" x2="60" y2="70" stroke="url(#gradient2)" strokeWidth="1" opacity="0.4" />
    <line x1="40" y1="70" x2="60" y2="70" stroke="url(#gradient2)" strokeWidth="1" opacity="0.4" />
    <line x1="25" y1="35" x2="30" y2="50" stroke="url(#gradient2)" strokeWidth="1" opacity="0.3" />
    <line x1="75" y1="35" x2="70" y2="50" stroke="url(#gradient2)" strokeWidth="1" opacity="0.3" />
    
    {/* P Letter */}
    <text x="50" y="58" fontSize="40" fontWeight="bold" fill="url(#gradient2)" textAnchor="middle" fontFamily="sans-serif">
      P
    </text>
  </svg>
);

// Logo Option 3: Geometric Structure (inspired by design 8)
export const LogoGeometric = ({ className = "w-10 h-10" }) => (
  <svg className={className} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#10b981" />
        <stop offset="100%" stopColor="#06b6d4" />
      </linearGradient>
    </defs>
    
    {/* Geometric structure */}
    <path d="M 50 15 L 80 75 L 20 75 Z" stroke="url(#gradient3)" strokeWidth="2" fill="none" opacity="0.3" />
    
    {/* Inner structural lines */}
    <line x1="50" y1="15" x2="50" y2="75" stroke="url(#gradient3)" strokeWidth="1" opacity="0.5" />
    <line x1="35" y1="45" x2="65" y2="45" stroke="url(#gradient3)" strokeWidth="1" opacity="0.5" />
    
    {/* Structural dots */}
    <circle cx="50" cy="15" r="3" fill="url(#gradient3)" />
    <circle cx="80" cy="75" r="3" fill="url(#gradient3)" />
    <circle cx="20" cy="75" r="3" fill="url(#gradient3)" />
    <circle cx="35" cy="45" r="2.5" fill="url(#gradient3)" />
    <circle cx="65" cy="45" r="2.5" fill="url(#gradient3)" />
    <circle cx="50" cy="60" r="2.5" fill="url(#gradient3)" />
    
    {/* P Letter */}
    <text x="50" y="58" fontSize="38" fontWeight="bold" fill="url(#gradient3)" textAnchor="middle" fontFamily="sans-serif">
      P
    </text>
  </svg>
);

// Main Logo Component with all variants
const PeptigenLogos = () => {
  return (
    <div className="p-8 bg-gray-900 min-h-screen">
      <h1 className="text-white text-3xl font-bold mb-8 text-center">Peptigen Logo Options</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-6xl mx-auto">
        {/* Option 1 */}
        <div className="bg-gray-800 p-8 rounded-xl text-center">
          <div className="flex justify-center mb-6">
            <LogoMolecular className="w-32 h-32" />
          </div>
          <h2 className="text-white text-xl font-bold mb-2">Molecular Triangle</h2>
          <p className="text-gray-400 text-sm">Clean, geometric, molecular structure</p>
          <div className="mt-6 flex items-center justify-center space-x-3">
            <LogoMolecular className="w-12 h-12" />
            <div className="text-left">
              <div className="text-2xl font-bold text-white">Peptigen</div>
              <div className="text-xs text-gray-400">Advanced Research</div>
            </div>
          </div>
        </div>
        
        {/* Option 2 */}
        <div className="bg-gray-800 p-8 rounded-xl text-center">
          <div className="flex justify-center mb-6">
            <LogoNetwork className="w-32 h-32" />
          </div>
          <h2 className="text-white text-xl font-bold mb-2">Complex Network</h2>
          <p className="text-gray-400 text-sm">Dynamic, interconnected, biological</p>
          <div className="mt-6 flex items-center justify-center space-x-3">
            <LogoNetwork className="w-12 h-12" />
            <div className="text-left">
              <div className="text-2xl font-bold text-white">Peptigen</div>
              <div className="text-xs text-gray-400">Advanced Research</div>
            </div>
          </div>
        </div>
        
        {/* Option 3 */}
        <div className="bg-gray-800 p-8 rounded-xl text-center">
          <div className="flex justify-center mb-6">
            <LogoGeometric className="w-32 h-32" />
          </div>
          <h2 className="text-white text-xl font-bold mb-2">Precision Structure</h2>
          <p className="text-gray-400 text-sm">Architectural, precise, advanced</p>
          <div className="mt-6 flex items-center justify-center space-x-3">
            <LogoGeometric className="w-12 h-12" />
            <div className="text-left">
              <div className="text-2xl font-bold text-white">Peptigen</div>
              <div className="text-xs text-gray-400">Advanced Research</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Color variations */}
      <div className="mt-16 text-center">
        <h2 className="text-white text-2xl font-bold mb-8">Size Variations</h2>
        <div className="bg-white p-8 rounded-xl inline-block">
          <div className="flex items-center justify-center space-x-8">
            <LogoMolecular className="w-8 h-8" />
            <LogoMolecular className="w-12 h-12" />
            <LogoMolecular className="w-16 h-16" />
            <LogoMolecular className="w-24 h-24" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PeptigenLogos;

import React, { useState, useEffect } from 'react';
import { AlertTriangle, X } from 'lucide-react';

const RegulatoryBanner = () => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Check if user has previously closed the banner
    const bannerClosed = localStorage.getItem('regulatoryBannerClosed');
    if (bannerClosed === 'true') {
      setIsVisible(false);
    }
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    localStorage.setItem('regulatoryBannerClosed', 'true');
  };

  if (!isVisible) return null;

  return (
    <div className="bg-yellow-500 text-gray-900 relative z-50" data-testid="regulatory-banner">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1">
            <AlertTriangle className="w-6 h-6 flex-shrink-0" />
            <div className="text-sm sm:text-base font-semibold">
              <span className="block sm:inline">
                <strong>FOR RESEARCH USE ONLY</strong> - Not for human consumption, veterinary use, or diagnostic purposes.
              </span>
              <span className="hidden md:inline ml-2">
                All products are intended for laboratory and research applications only.
              </span>
            </div>
          </div>
          <button
            onClick={handleClose}
            data-testid="close-regulatory-banner"
            className="p-1 hover:bg-yellow-600 rounded transition-colors flex-shrink-0"
            aria-label="Close regulatory notice"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default RegulatoryBanner;

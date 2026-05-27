import React from 'react';
import { AlertTriangle } from 'lucide-react';

const UpdateNoticeBanner = () => {
  return (
    <div
      className="bg-red-600 text-white relative z-50 border-b border-red-800"
      data-testid="update-notice-banner"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5">
        <div className="flex items-center justify-center gap-3 text-center">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 animate-pulse" />
          <p className="text-xs sm:text-sm font-semibold leading-snug">
            <span className="hidden sm:inline">SITE UNDER UPDATE — </span>
            <span className="sm:hidden">UPDATING — </span>
            New protocols are being added. You may experience temporary instability or missing protocols.
          </p>
          <AlertTriangle className="w-5 h-5 flex-shrink-0 animate-pulse hidden sm:block" />
        </div>
      </div>
    </div>
  );
};

export default UpdateNoticeBanner;

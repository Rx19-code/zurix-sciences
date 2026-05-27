import React from 'react';
import { AlertTriangle } from 'lucide-react';

const UpdateNoticeBanner = () => {
  const message = 'SITE UNDER UPDATE — New protocols are being added. You may experience temporary instability or missing protocols.';

  // Repeat the message a few times so the scroll loop never shows a gap
  const items = Array.from({ length: 6 });

  return (
    <div
      className="bg-red-600 text-white relative z-50 border-b border-red-800 overflow-hidden"
      data-testid="update-notice-banner"
    >
      <div className="py-2.5">
        <div className="marquee-track flex whitespace-nowrap">
          {items.map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-3 px-8 text-xs sm:text-sm font-semibold tracking-wide"
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{message}</span>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes zurix-marquee {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .marquee-track {
          width: max-content;
          animation: zurix-marquee 40s linear infinite;
          will-change: transform;
        }
        .marquee-track:hover {
          animation-play-state: paused;
        }
        @media (prefers-reduced-motion: reduce) {
          .marquee-track { animation: none; }
        }
      `}</style>
    </div>
  );
};

export default UpdateNoticeBanner;

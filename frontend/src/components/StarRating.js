import React, { useState, useEffect } from 'react';
import { Star } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

var API = process.env.REACT_APP_BACKEND_URL;

/**
 * Star rating widget — read + write.
 * Props: hubSlug, protocolId, initialAvg, initialCount
 */
export default function StarRating({ hubSlug, protocolId, initialAvg = 0, initialCount = 0, size = 'md' }) {
  var { token, user } = useAuth();
  var [avg, setAvg] = useState(initialAvg);
  var [count, setCount] = useState(initialCount);
  var [myRating, setMyRating] = useState(0);
  var [hover, setHover] = useState(0);
  var [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetch(API + '/api/hubs/' + hubSlug + '/protocols/' + protocolId + '/my-rating', {
      headers: { Authorization: 'Bearer ' + token },
    })
      .then(r => r.json())
      .then(d => { if (d.your_rating) setMyRating(d.your_rating); })
      .catch(() => {});
  }, [hubSlug, protocolId, token]);

  function submit(stars) {
    if (!token) return;
    setSubmitting(true);
    fetch(API + '/api/hubs/' + hubSlug + '/protocols/' + protocolId + '/rate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
      body: JSON.stringify({ stars: stars }),
    })
      .then(r => r.json())
      .then(d => {
        if (d.success) {
          setAvg(d.rating_avg);
          setCount(d.rating_count);
          setMyRating(stars);
        }
      })
      .catch(() => {})
      .finally(() => setSubmitting(false));
  }

  var iconSize = size === 'lg' ? 'w-6 h-6' : (size === 'sm' ? 'w-3.5 h-3.5' : 'w-5 h-5');
  var displayed = hover || myRating || Math.round(avg);
  var canRate = !!user;

  return (
    <div className="flex items-center gap-2" data-testid={`star-rating-${protocolId}`}>
      <div className="flex items-center gap-0.5" onMouseLeave={() => setHover(0)}>
        {[1, 2, 3, 4, 5].map(n => (
          <button
            key={n}
            type="button"
            disabled={!canRate || submitting}
            onMouseEnter={() => canRate && setHover(n)}
            onClick={() => canRate && submit(n)}
            data-testid={`star-${n}`}
            className={'transition-transform ' + (canRate ? 'hover:scale-110 cursor-pointer' : 'cursor-default')}
            title={canRate ? `Rate ${n} star${n > 1 ? 's' : ''}` : 'Sign in to rate'}
          >
            <Star
              className={iconSize + ' transition-colors ' + (n <= displayed ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300')}
            />
          </button>
        ))}
      </div>
      <span className="text-xs text-gray-500 font-medium">
        {avg > 0 ? avg.toFixed(1) : 'No ratings'}
        {count > 0 && <span className="text-gray-400"> ({count})</span>}
      </span>
    </div>
  );
}

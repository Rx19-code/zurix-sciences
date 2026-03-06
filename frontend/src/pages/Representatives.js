import React, { useEffect, useState } from 'react';
import { MessageCircle, MapPin, Shield } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Country codes for flag images (ISO 3166-1 alpha-2)
const countryCodeMap = {
  'Paraguay': 'py',
  'United States': 'us',
  'Switzerland': 'ch',
  'Brazil': 'br',
  'Argentina': 'ar',
  'Mexico': 'mx',
  'Colombia': 'co',
  'Chile': 'cl',
  'Peru': 'pe',
  'Uruguay': 'uy',
  'Canada': 'ca',
  'UK': 'gb',
  'Germany': 'de',
  'Spain': 'es',
  'France': 'fr',
  'Italy': 'it',
  'Portugal': 'pt',
  'Australia': 'au',
  'Netherlands': 'nl',
  'Belgium': 'be',
  'Japan': 'jp',
  'South Korea': 'kr',
  'China': 'cn',
  'India': 'in',
  'Russia': 'ru',
  'South Africa': 'za',
};

// Flag component using flagcdn.com
const FlagIcon = ({ country, size = 80 }) => {
  const countryCode = countryCodeMap[country]?.toLowerCase() || 'un';
  
  return (
    <img
      src={`https://flagcdn.com/w${size}/${countryCode}.png`}
      srcSet={`https://flagcdn.com/w${size * 2}/${countryCode}.png 2x`}
      width={size}
      height={Math.round(size * 0.75)}
      alt={`${country} flag`}
      className="rounded shadow-sm mx-auto"
      style={{ objectFit: 'cover' }}
      onError={(e) => {
        // Fallback to a placeholder if flag not found
        e.target.style.display = 'none';
      }}
    />
  );
};

const Representatives = () => {
  const [representatives, setRepresentatives] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRepresentatives();
  }, []);

  const fetchRepresentatives = async () => {
    try {
      const response = await axios.get(`${API}/representatives`);
      setRepresentatives(response.data);
    } catch (error) {
      console.error('Error fetching representatives:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWhatsApp = (whatsapp) => {
    const message = encodeURIComponent('Hello! I am interested in Zurix Sciences products.');
    window.open(`https://wa.me/${whatsapp.replace(/\D/g, '')}?text=${message}`, '_blank');
  };

  const handleThreema = (threemaId) => {
    window.open(`https://threema.id/${threemaId}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="representatives-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4" data-testid="representatives-title">
            Our Representatives
          </h1>
          <p className="text-xl text-gray-600">
            Connect with your local representative for personalized service and support
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {representatives.map((rep) => (
              <div
                key={rep.id}
                className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow p-8"
                data-testid={`rep-card-${rep.country}`}
              >
                {/* Country Flag */}
                <div className="text-center mb-6">
                  <div className="mb-4">
                    <FlagIcon country={rep.country} size={80} />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-1" data-testid="rep-country">{rep.country}</h2>
                  <p className="text-gray-600">{rep.region}</p>
                </div>

                {/* Representative Info */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 text-gray-700">
                    <MapPin className="w-5 h-5 text-blue-600 flex-shrink-0" />
                    <span className="font-semibold" data-testid="rep-name">{rep.name}</span>
                  </div>
                  {rep.whatsapp && (
                    <div className="flex items-center space-x-3 text-gray-700">
                      <MessageCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <span className="font-mono text-sm">{rep.whatsapp}</span>
                    </div>
                  )}
                  {rep.threema && (
                    <div className="flex items-center space-x-3 text-gray-700">
                      <Shield className="w-5 h-5 text-purple-600 flex-shrink-0" />
                      <span className="font-mono text-sm">ID: {rep.threema}</span>
                    </div>
                  )}
                </div>

                {/* Contact Buttons */}
                <div className="mt-6 space-y-3">
                  {rep.whatsapp && (
                    <button
                      onClick={() => handleWhatsApp(rep.whatsapp)}
                      data-testid={`contact-rep-${rep.country}`}
                      className="w-full flex items-center justify-center space-x-2 text-white font-semibold py-3 rounded-lg transition-colors"
                      style={{ backgroundColor: '#3D3D3D' }}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2D2D2D'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3D3D3D'}
                    >
                      <MessageCircle className="w-5 h-5 text-green-400" />
                      <span>WhatsApp</span>
                    </button>
                  )}
                  {rep.threema && (
                    <button
                      onClick={() => handleThreema(rep.threema)}
                      className="w-full flex items-center justify-center space-x-2 text-white font-semibold py-3 rounded-lg transition-colors"
                      style={{ backgroundColor: '#3D3D3D' }}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2D2D2D'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3D3D3D'}
                    >
                      <Shield className="w-5 h-5 text-green-400" />
                      <span>Threema</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Section */}
        <div className="mt-16 bg-blue-50 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full font-bold text-xl mb-4">
                1
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Select Your Region</h3>
              <p className="text-gray-600 text-sm">
                Choose the representative for your country or region
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full font-bold text-xl mb-4">
                2
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Make Contact</h3>
              <p className="text-gray-600 text-sm">
                Reach out via WhatsApp or Threema with your order
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full font-bold text-xl mb-4">
                3
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Get Support</h3>
              <p className="text-gray-600 text-sm">
                Receive personalized service and shipping details
              </p>
            </div>
          </div>
        </div>

        {/* Payment Info */}
        <div className="mt-8 bg-white rounded-2xl shadow-sm p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 text-center">Payment Information</h2>
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-6">
            <p className="text-amber-800 text-center">
              <strong>Important:</strong> Payment methods and terms vary by region and are determined by each local representative.
            </p>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">Common Payment Options</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { name: 'Bitcoin (BTC)', desc: 'Cryptocurrency' },
              { name: 'Monero (XMR)', desc: 'Private cryptocurrency' },
              { name: 'USDT', desc: 'Stablecoin' },
              { name: 'Bank Transfer', desc: 'Wire transfer' }
            ].map((method, index) => (
              <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="font-semibold text-gray-900 mb-1">{method.name}</p>
                <p className="text-xs text-gray-600">{method.desc}</p>
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-gray-500 mt-6">
            Please contact your regional representative for specific payment options, terms, and wallet addresses available in your area.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Representatives;

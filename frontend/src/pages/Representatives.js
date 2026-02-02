import React, { useEffect, useState } from 'react';
import { MessageCircle, Mail, MapPin } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    const message = encodeURIComponent('Hello! I am interested in RX Research Sciences products.');
    window.open(`https://wa.me/${whatsapp.replace(/\D/g, '')}?text=${message}`, '_blank');
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
                {/* Flag */}
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full mb-4">
                    <span className="text-5xl">{rep.flag_emoji}</span>
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
                  <div className="flex items-center space-x-3 text-gray-700">
                    <MessageCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                    <span className="font-mono text-sm">{rep.whatsapp}</span>
                  </div>
                </div>

                {/* Contact Button */}
                <button
                  onClick={() => handleWhatsApp(rep.whatsapp)}
                  data-testid={`contact-rep-${rep.country}`}
                  className="mt-6 w-full flex items-center justify-center space-x-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  <MessageCircle className="w-5 h-5" />
                  <span>Contact via WhatsApp</span>
                </button>
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
                Reach out via WhatsApp or email with your order
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
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Accepted Payment Methods</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { name: 'Bitcoin (BTC)', desc: 'Most popular cryptocurrency' },
              { name: 'USDT', desc: 'Tether - Stablecoin' },
              { name: 'Solana (SOL)', desc: 'Fast & low fees' },
              { name: 'Ethereum (ETH)', desc: 'ERC-20 tokens' }
            ].map((crypto, index) => (
              <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="font-semibold text-gray-900 mb-1">{crypto.name}</p>
                <p className="text-xs text-gray-600">{crypto.desc}</p>
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-gray-500 mt-6">
            Your representative will provide payment details and wallet addresses
          </p>
        </div>
      </div>
    </div>
  );
};

export default Representatives;
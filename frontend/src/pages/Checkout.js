import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, MessageCircle, Check, Shield } from 'lucide-react';
import axios from 'axios';
import { useCart } from '../context/CartContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Checkout = () => {
  const navigate = useNavigate();
  const { cart, getTotal, clearCart } = useCart();
  const [representatives, setRepresentatives] = useState([]);
  const [selectedRep, setSelectedRep] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (cart.length === 0) {
      navigate('/products');
      return;
    }
    fetchRepresentatives();
  }, [cart, navigate]);

  const fetchRepresentatives = async () => {
    try {
      const response = await axios.get(`${API}/representatives`);
      setRepresentatives(response.data);
      if (response.data.length > 0) {
        setSelectedRep(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching representatives:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = (e) => {
    e.preventDefault();

    const rep = representatives.find(r => r.id === selectedRep);
    if (!rep) return;

    // Build order message
    let message = `*New Order from Zurix Sciences*\n\n`;
    message += `*Customer Information:*\n`;
    message += `Name: ${customerName}\n`;
    message += `Email: ${customerEmail}\n\n`;
    message += `*Order Details:*\n`;
    
    cart.forEach((item, index) => {
      message += `\n${index + 1}. ${item.name}\n`;
      message += `   - Quantity: ${item.quantity}\n`;
      message += `   - Price: $${item.price.toFixed(2)} each\n`;
      message += `   - Subtotal: $${(item.price * item.quantity).toFixed(2)}\n`;
    });

    message += `\n*Total: $${getTotal().toFixed(2)}*\n`;
    
    if (notes) {
      message += `\n*Additional Notes:*\n${notes}\n`;
    }

    message += `\n_Please confirm availability and payment details._`;

    // Encode message
    const encodedMessage = encodeURIComponent(message);
    
    // Check if rep has WhatsApp or Threema
    if (rep.whatsapp && rep.whatsapp.trim() !== '') {
      const whatsappUrl = `https://wa.me/${rep.whatsapp.replace(/\D/g, '')}?text=${encodedMessage}`;
      window.open(whatsappUrl, '_blank');
    } else if (rep.threema) {
      const threemaUrl = `https://threema.id/${rep.threema}?text=${encodedMessage}`;
      window.open(threemaUrl, '_blank');
    }

    // Clear cart and redirect
    clearCart();
    navigate('/checkout/success');
  };
  
  // Get selected representative
  const getSelectedRep = () => representatives.find(r => r.id === selectedRep);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="checkout-page">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8" data-testid="checkout-title">Checkout</h1>

        <form onSubmit={handleCheckout} className="space-y-6">
          {/* Customer Information */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Customer Information</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  id="name"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  data-testid="customer-name-input"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  id="email"
                  value={customerEmail}
                  onChange={(e) => setCustomerEmail(e.target.value)}
                  data-testid="customer-email-input"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
          </div>

          {/* Select Representative */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Select Your Representative</h2>
            <div className="space-y-3">
              {representatives.map((rep) => (
                <label
                  key={rep.id}
                  className={`flex items-center space-x-4 p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                    selectedRep === rep.id
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  data-testid={`rep-option-${rep.country}`}
                >
                  <input
                    type="radio"
                    name="representative"
                    value={rep.id}
                    checked={selectedRep === rep.id}
                    onChange={(e) => setSelectedRep(e.target.value)}
                    className="w-5 h-5 text-blue-600"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{rep.flag_emoji}</span>
                      <div>
                        <p className="font-semibold text-gray-900">{rep.country}</p>
                        <p className="text-sm text-gray-600">{rep.name}</p>
                      </div>
                    </div>
                  </div>
                  {selectedRep === rep.id && (
                    <Check className="w-6 h-6 text-blue-600" />
                  )}
                </label>
              ))}
            </div>
          </div>

          {/* Order Summary */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>
            <div className="space-y-3 mb-4">
              {cart.map((item) => (
                <div key={item.id} className="flex justify-between items-start py-3 border-b" data-testid={`checkout-item-${item.id}`}>
                  <div>
                    <p className="font-semibold text-gray-900">{item.name}</p>
                    <p className="text-sm text-gray-600">Quantity: {item.quantity}</p>
                  </div>
                  <p className="font-semibold text-gray-900">
                    ${(item.price * item.quantity).toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center text-lg font-bold pt-4 border-t">
              <span>Total:</span>
              <span className="text-blue-600" data-testid="checkout-total">${getTotal().toFixed(2)}</span>
            </div>
          </div>

          {/* Additional Notes */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Additional Notes (Optional)</h2>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              data-testid="notes-textarea"
              placeholder="Any special requests or questions?"
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Submit Button */}
          {(() => {
            const rep = getSelectedRep();
            const isThreema = rep && (!rep.whatsapp || rep.whatsapp.trim() === '') && rep.threema;
            return (
              <>
                <button
                  type="submit"
                  data-testid="submit-order-button"
                  className="w-full flex items-center justify-center space-x-2 text-white font-semibold py-4 rounded-lg transition-colors"
                  style={{ backgroundColor: '#3D3D3D' }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2D2D2D'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3D3D3D'}
                >
                  {isThreema ? (
                    <>
                      <Shield className="w-5 h-5 text-green-400" />
                      <span>Send Order via Threema</span>
                    </>
                  ) : (
                    <>
                      <MessageCircle className="w-5 h-5 text-green-400" />
                      <span>Send Order via WhatsApp</span>
                    </>
                  )}
                </button>

                <p className="text-sm text-gray-500 text-center">
                  You will be redirected to {isThreema ? 'Threema' : 'WhatsApp'} to complete your order with your representative
                </p>
              </>
            );
          })()}
        </form>
      </div>
    </div>
  );
};

export default Checkout;
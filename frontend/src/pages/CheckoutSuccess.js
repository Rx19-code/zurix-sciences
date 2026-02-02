import React from 'react';
import { CheckCircle, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

const CheckoutSuccess = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center" data-testid="checkout-success-page">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4" data-testid="success-title">
            Order Sent Successfully!
          </h1>
          <p className="text-gray-600 mb-8">
            Your order has been sent to your representative via WhatsApp. They will contact you shortly to confirm availability and payment details.
          </p>
          <div className="space-y-3">
            <Link
              to="/"
              data-testid="home-button"
              className="flex items-center justify-center space-x-2 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors"
            >
              <Home className="w-5 h-5" />
              <span>Back to Home</span>
            </Link>
            <Link
              to="/products"
              data-testid="continue-shopping-button"
              className="block w-full text-blue-600 hover:text-blue-700 font-medium py-3"
            >
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutSuccess;
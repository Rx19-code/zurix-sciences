import React from 'react';
import { Link } from 'react-router-dom';
import { Bitcoin, Shield, TrendingUp, Users } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-gray-300" data-testid="main-footer">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <img 
                src="/assets/nexgen-logo-new.png" 
                alt="Nexgen Sciences Research Logo" 
                className="w-12 h-12"
              />
              <h3 className="text-white font-bold text-lg">Nexgen Sciences</h3>
            </div>
            <p className="text-sm text-gray-400">
              Premium research compounds and peptides for scientific studies. Committed to quality and purity.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/products" className="hover:text-blue-400 transition-colors">Products</Link></li>
              <li><Link to="/calculator" className="hover:text-blue-400 transition-colors">Dosage Calculator</Link></li>
              <li><Link to="/verify" className="hover:text-blue-400 transition-colors">Verify Product</Link></li>
              <li><Link to="/representatives" className="hover:text-blue-400 transition-colors">Representatives</Link></li>
              <li><Link to="/contact" className="hover:text-blue-400 transition-colors">Contact Us</Link></li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-white font-semibold mb-4">Why Choose Us</h4>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start space-x-2">
                <Shield className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <span>99%+ HPLC Purity</span>
              </li>
              <li className="flex items-start space-x-2">
                <Users className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <span>Local Support</span>
              </li>
              <li className="flex items-start space-x-2">
                <Bitcoin className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <span>Crypto Payments</span>
              </li>
              <li className="flex items-start space-x-2">
                <TrendingUp className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <span>Scientific Support</span>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4">Contact</h4>
            <p className="text-sm text-gray-400 mb-4">
              For research inquiries and orders, please contact your local representative.
            </p>
            <Link
              to="/representatives"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
              data-testid="footer-find-representative-btn"
            >
              Find Your Representative
            </Link>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-800 text-center">
          <p className="text-sm text-gray-500">
            © {new Date().getFullYear()} Nexgen Sciences Research. For research purposes only. Not for human consumption.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
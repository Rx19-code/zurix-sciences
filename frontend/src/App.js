import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation, useSearchParams } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import RegulatoryBanner from './components/RegulatoryBanner';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Calculator from './pages/Calculator';
import Verify from './pages/Verify';
import Checkout from './pages/Checkout';
import CheckoutSuccess from './pages/CheckoutSuccess';
import Representatives from './pages/Representatives';
import Contact from './pages/Contact';
import Protocols from './pages/Library';
import Library from './pages/Library';
import PeptideDetailPage from './pages/PeptideDetail';
import PeptigenLogos from './components/PeptigenLogos';
import Admin from './pages/Admin';
import './App.css';

// Layout wrapper that hides navbar/footer for admin
function Layout({ children }) {
  const location = useLocation();
  const isAdmin = location.pathname === '/admin';
  
  if (isAdmin) {
    return <>{children}</>;
  }
  
  return (
    <div className="flex flex-col min-h-screen">
      <RegulatoryBanner />
      <Navbar />
      <main className="flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  );
}

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function MaintenancePage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      padding: '20px'
    }}>
      <div style={{ textAlign: 'center', maxWidth: '500px' }}>
        <div style={{ fontSize: '64px', marginBottom: '24px' }}>
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="1.5" style={{margin: '0 auto'}}>
            <path d="M12 6V12L16 14" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="12" cy="12" r="10" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <h1 style={{
          color: '#f8fafc',
          fontSize: '32px',
          fontWeight: '700',
          marginBottom: '12px',
          letterSpacing: '-0.5px'
        }}>
          Zurix Sciences
        </h1>
        <p style={{
          color: '#94a3b8',
          fontSize: '18px',
          lineHeight: '1.6',
          marginBottom: '32px'
        }}>
          We are currently updating our website to serve you better.<br/>
          We'll be back soon!
        </p>
        <div style={{
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '12px',
          padding: '16px 24px',
          color: '#60a5fa',
          fontSize: '14px'
        }}>
          For urgent inquiries, contact us at <strong>support@zurixsciences.com</strong>
        </div>
      </div>
    </div>
  );
}

function AppContent() {
  var [maintenance, setMaintenance] = useState(false);
  var [checked, setChecked] = useState(false);
  var [searchParams] = useSearchParams();
  var bypass = searchParams.get('bypass') === 'zurix2026';

  useEffect(function() {
    fetch((BACKEND_URL || '') + '/api/maintenance')
      .then(function(r) { return r.json(); })
      .then(function(d) { setMaintenance(d.maintenance); setChecked(true); })
      .catch(function() { setChecked(true); });
  }, []);

  if (!checked) return null;
  if (maintenance && !bypass) return <MaintenancePage />;

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetail />} />
        <Route path="/calculator" element={<Calculator />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/checkout/success" element={<CheckoutSuccess />} />
        <Route path="/representatives" element={<Representatives />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/protocols" element={<Protocols />} />
        <Route path="/protocols/:slug" element={<PeptideDetailPage />} />
        <Route path="/library" element={<Library />} />
        <Route path="/library/:slug" element={<PeptideDetailPage />} />
        <Route path="/logos" element={<PeptigenLogos />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <CartProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </CartProvider>
  );
}

export default App;

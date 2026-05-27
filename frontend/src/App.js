import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation, useSearchParams } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import { AuthProvider } from './context/AuthContext';
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
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import AuthCallback from './pages/AuthCallback';
import StackDetail from './pages/StackDetail';
import HubDetail from './pages/HubDetail';
import MaintenancePage from './pages/Maintenance';
import './App.css';

// Layout wrapper that hides navbar/footer for admin and login
function Layout({ children }) {
  const location = useLocation();
  const isAdmin = location.pathname === '/admin';
  const isLogin = location.pathname === '/login';
  const isCallback = location.pathname === '/auth/callback';
  const isForgot = location.pathname === '/forgot-password';
  const isReset = location.pathname === '/reset-password';
  
  if (isAdmin || isLogin || isCallback || isForgot || isReset) {
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

function AppRouter() {
  var location = useLocation();

  // Check URL fragment for session_id - MUST be synchronous during render
  if (location.hash && location.hash.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
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
      <Route path="/protocols/stack/:slug" element={<StackDetail />} />
      <Route path="/stacks/:slug" element={<HubDetail />} />
      <Route path="/protocols/:slug" element={<PeptideDetailPage />} />
      <Route path="/library" element={<Library />} />
      <Route path="/library/:slug" element={<PeptideDetailPage />} />
      <Route path="/logos" element={<PeptigenLogos />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/login" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
    </Routes>
  );
}

function AppContent() {
  var [maintenance, setMaintenance] = useState(false);
  var [bypassed, setBypassed] = useState(false);
  var [checked, setChecked] = useState(false);
  var [searchParams] = useSearchParams();
  var legacyBypass = searchParams.get('bypass') === 'zurix2026';

  useEffect(function() {
    fetch((BACKEND_URL || '') + '/api/maintenance/status', { credentials: 'include' })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        setMaintenance(!!d.active);
        setBypassed(!!d.bypass);
        setChecked(true);
      })
      .catch(function() {
        // Fallback to legacy endpoint
        fetch((BACKEND_URL || '') + '/api/maintenance')
          .then(function(r) { return r.json(); })
          .then(function(d) { setMaintenance(!!d.maintenance); setChecked(true); })
          .catch(function() { setChecked(true); });
      });
  }, []);

  if (!checked) return null;
  if (maintenance && !bypassed && !legacyBypass) return <MaintenancePage />;

  return (
    <Layout>
      <AppRouter />
    </Layout>
  );
}

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;

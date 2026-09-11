import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Shield, Users, Bitcoin, TrendingUp, Beaker, Brain, Pill, ChevronLeft, ChevronRight, ShieldCheck, Layers } from 'lucide-react';
import axios from 'axios';
import ProductCard from '../components/ProductCard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [slide, setSlide] = useState(0);

  const slides = [
    {
      bg: 'https://images.unsplash.com/photo-1773984203485-8ac6e4ddadfa?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600',
      badge: null,
      title: 'Premium Research Compounds',
      subtitle: 'High-purity peptides, GLP-1 analogs, and research chemicals for scientific studies and laboratory research.',
      primary: { label: 'Browse Products', to: '/products', icon: ArrowRight },
      secondary: { label: 'Verify Product', to: '/verify', icon: ShieldCheck },
    },
    {
      bg: 'https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600',
      badge: 'Anti-Counterfeit Technology',
      title: 'Verified Authenticity',
      subtitle: 'Every vial ships with a unique QR code. Scan it to instantly confirm your product is genuine Zurix Sciences.',
      primary: { label: 'Verify a Product', to: '/verify', icon: ShieldCheck },
      secondary: { label: 'Browse Products', to: '/products', icon: ArrowRight },
    },
    {
      bg: 'https://images.unsplash.com/photo-1637929476734-bd7f5f78e40a?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600',
      badge: 'Lifetime Access',
      title: 'Clinical Stack Protocols',
      subtitle: 'Evidence-based dosing, cycles and synergies for every peptide — curated by our research team in the Stack Library.',
      primary: { label: 'Explore Protocols', to: '/protocols', icon: Layers },
      secondary: { label: 'Browse Products', to: '/products', icon: ArrowRight },
    },
  ];

  useEffect(() => {
    const timer = setInterval(() => setSlide((s) => (s + 1) % slides.length), 6000);
    return () => clearInterval(timer);
  }, [slides.length]);

  useEffect(() => {
    const fetchFeaturedProducts = async () => {
      try {
        const response = await axios.get(`${API}/products?featured=true`);
        setFeaturedProducts(response.data.slice(0, 6));
      } catch (error) {
        console.error('Error fetching featured products:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFeaturedProducts();
  }, []);

  const categories = [
    {
      name: 'GLP-1 Analogs',
      description: 'Tirzepatide, Retatrutide for metabolic research',
      icon: Pill,
      color: 'from-blue-500 to-blue-600'
    },
    {
      name: 'Research Peptides',
      description: 'BPC-157, TB-500, Epithalon for tissue repair',
      icon: Beaker,
      color: 'from-green-500 to-green-600'
    },
    {
      name: 'Cognitive Enhancers',
      description: 'Semax, Selank, Noopept for neurological research',
      icon: Brain,
      color: 'from-purple-500 to-purple-600'
    },
    {
      name: 'Coenzymes',
      description: 'NAD+, NMN, CoQ10 for cellular energy',
      icon: TrendingUp,
      color: 'from-orange-500 to-orange-600'
    }
  ];

  const features = [
    {
      icon: Shield,
      title: '99%+ HPLC Purity',
      description: 'All compounds verified by HPLC for maximum purity and consistency.'
    },
    {
      icon: Users,
      title: 'Local Support',
      description: 'Dedicated representatives in each country for personalized service.'
    },
    {
      icon: Bitcoin,
      title: 'Crypto Payments',
      description: 'Secure, anonymous payments with major cryptocurrencies.'
    },
    {
      icon: TrendingUp,
      title: 'Scientific Support',
      description: 'Access to our team of researchers for technical questions.'
    }
  ];

  return (
    <div data-testid="home-page">
      {/* Hero Slider */}
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white overflow-hidden" data-testid="hero-section">
        {slides.map((s, i) => (
          <div
            key={i}
            className="absolute inset-0 bg-cover bg-center transition-opacity duration-700 ease-in-out"
            style={{ backgroundImage: `url('${s.bg}')`, opacity: i === slide ? 0.16 : 0, backgroundBlendMode: 'overlay' }}
          />
        ))}

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 min-h-[420px] sm:min-h-[480px] flex items-center">
          {slides.map((s, i) => {
            const PIcon = s.primary.icon;
            const SIcon = s.secondary.icon;
            return (
              <div
                key={i}
                data-testid={`hero-slide-${i}`}
                className={`w-full text-center transition-all duration-700 ${i === slide ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none absolute inset-x-0'}`}
                aria-hidden={i !== slide}
              >
                {s.badge && (
                  <span className="inline-flex items-center gap-2 px-4 py-1.5 mb-5 rounded-full bg-white/10 border border-white/20 text-blue-100 text-sm font-medium backdrop-blur-sm">
                    <ShieldCheck className="w-4 h-4" /> {s.badge}
                  </span>
                )}
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6" data-testid={i === slide ? 'hero-title' : undefined}>
                  {s.title}
                </h1>
                <p className="text-xl sm:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
                  {s.subtitle}
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link
                    to={s.primary.to}
                    data-testid={`hero-primary-btn-${i}`}
                    className="inline-flex items-center space-x-2 bg-white text-blue-900 font-semibold px-8 py-3 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    <span>{s.primary.label}</span>
                    <PIcon className="w-5 h-5" />
                  </Link>
                  <Link
                    to={s.secondary.to}
                    data-testid={`hero-secondary-btn-${i}`}
                    className="inline-flex items-center space-x-2 bg-blue-700 hover:bg-blue-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
                  >
                    <span>{s.secondary.label}</span>
                    <SIcon className="w-5 h-5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>

        {/* Arrows */}
        <button
          onClick={() => setSlide((slide - 1 + slides.length) % slides.length)}
          data-testid="hero-prev-btn"
          aria-label="Previous slide"
          className="absolute left-3 sm:left-6 top-1/2 -translate-y-1/2 z-20 w-11 h-11 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-sm transition-colors"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button
          onClick={() => setSlide((slide + 1) % slides.length)}
          data-testid="hero-next-btn"
          aria-label="Next slide"
          className="absolute right-3 sm:right-6 top-1/2 -translate-y-1/2 z-20 w-11 h-11 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-sm transition-colors"
        >
          <ChevronRight className="w-6 h-6" />
        </button>

        {/* Dots */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2.5">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => setSlide(i)}
              data-testid={`hero-dot-${i}`}
              aria-label={`Go to slide ${i + 1}`}
              className={`h-2.5 rounded-full transition-all ${i === slide ? 'w-8 bg-white' : 'w-2.5 bg-white/40 hover:bg-white/70'}`}
            />
          ))}
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 bg-gray-50" data-testid="categories-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Research Categories</h2>
            <p className="text-lg text-gray-600">Explore our specialized research compounds and peptides</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {categories.map((category, index) => {
              const Icon = category.icon;
              return (
                <Link
                  key={index}
                  to={`/products?category=${encodeURIComponent(category.name)}`}
                  className="group bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden"
                  data-testid={`category-card-${index}`}
                >
                  <div className="p-6">
                    <div className={`w-12 h-12 bg-gradient-to-br ${category.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                      {category.name}
                    </h3>
                    <p className="text-sm text-gray-600">{category.description}</p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="py-16" data-testid="featured-products-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Featured Products</h2>
            <p className="text-lg text-gray-600">Our most popular research compounds</p>
          </div>
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {featuredProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
              <div className="text-center">
                <Link
                  to="/products"
                  className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-semibold"
                  data-testid="view-all-products-link"
                >
                  <span>View All Products</span>
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </div>
            </>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50" data-testid="features-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Why Choose Zurix Sciences</h2>
            <p className="text-lg text-gray-600">Quality, reliability, and scientific excellence in every compound</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="text-center" data-testid={`feature-${index}`}>
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                    <Icon className="w-8 h-8 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-blue-800 text-white" data-testid="cta-section">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">Ready to Start Your Research?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Connect with your local representative for personalized service and support.
          </p>
          <Link
            to="/representatives"
            data-testid="find-representative-btn"
            className="inline-flex items-center space-x-2 bg-white text-blue-900 font-semibold px-8 py-3 rounded-lg hover:bg-blue-50 transition-colors"
          >
            <span>Find Your Representative</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Shield, Users, Bitcoin, TrendingUp, Beaker, Brain, Pill } from 'lucide-react';
import axios from 'axios';
import ProductCard from '../components/ProductCard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

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
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white overflow-hidden" data-testid="hero-section">
        {/* Background Image with Opacity - Molecular Structure */}
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-[0.13]"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1740666387475-548de5c37691?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwyfHxwZXB0aWRlJTIwc3RydWN0dXJlfGVufDB8fHx8MTc3MDA3NTg5Mnww&ixlib=rb-4.1.0&q=85')",
            backgroundBlendMode: 'overlay'
          }}
        />
        
        {/* Content */}
        <div className="relative z-10 w-full px-6 lg:px-12 py-12">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
            <div className="lg:w-1/2">
              <h1 className="text-4xl lg:text-5xl font-bold mb-3 leading-tight" data-testid="hero-title">
                Premium Research Compounds
              </h1>
              <p className="text-lg text-blue-100 mb-5">
                High-purity peptides, GLP-1 analogs, and research chemicals for scientific studies and laboratory research.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link
                  to="/products"
                  data-testid="browse-products-btn"
                  className="inline-flex items-center space-x-2 bg-white text-blue-900 font-semibold px-6 py-3 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  <span>Browse Products</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/verify"
                  data-testid="verify-product-btn"
                  className="inline-flex items-center space-x-2 bg-blue-700 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
                >
                  <span>Verify Product</span>
                </Link>
              </div>
            </div>
            <div className="lg:w-1/2 flex justify-center lg:justify-end">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold">99%+</p>
                  <p className="text-sm text-blue-200">HPLC Purity</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold">50+</p>
                  <p className="text-sm text-blue-200">Products</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold">24/7</p>
                  <p className="text-sm text-blue-200">Support</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold">BTC</p>
                  <p className="text-sm text-blue-200">Crypto Pay</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-10 bg-gray-50" data-testid="categories-section">
        <div className="w-full px-6 lg:px-12">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between mb-6 gap-3">
            <div>
              <h2 className="text-2xl lg:text-3xl font-bold text-gray-900">Research Categories</h2>
              <p className="text-gray-600">Explore our specialized research compounds and peptides</p>
            </div>
            <Link to="/products" className="text-blue-600 font-semibold hover:underline flex items-center gap-2">
              View All Products <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {categories.map((category, index) => {
              const Icon = category.icon;
              return (
                <Link
                  key={index}
                  to={`/products?category=${encodeURIComponent(category.name)}`}
                  className="group bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden"
                  data-testid={`category-card-${index}`}
                >
                  <div className="p-4">
                    <div className={`w-10 h-10 bg-gradient-to-br ${category.color} rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
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
      <section className="py-10" data-testid="featured-products-section">
        <div className="w-full px-6 lg:px-12">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between mb-6 gap-3">
            <div>
              <h2 className="text-2xl lg:text-3xl font-bold text-gray-900">Featured Products</h2>
              <p className="text-gray-600">Our most popular research compounds</p>
            </div>
            <Link to="/products" className="text-blue-600 font-semibold hover:underline flex items-center gap-2">
              View All Products <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-gray-300 border-t-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {featuredProducts.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-10 bg-gray-50" data-testid="features-section">
        <div className="w-full px-6 lg:px-12">
          <div className="mb-6">
            <h2 className="text-2xl lg:text-3xl font-bold text-gray-900">Why Choose Zurix Sciences</h2>
            <p className="text-gray-600">Quality, reliability, and scientific excellence in every compound</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="bg-white rounded-lg p-4 shadow-sm" data-testid={`feature-${index}`}>
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-3">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">{feature.title}</h3>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-10 bg-gradient-to-r from-blue-600 to-blue-800 text-white" data-testid="cta-section">
        <div className="w-full px-6 lg:px-12">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl lg:text-3xl font-bold mb-2">Ready to Start Your Research?</h2>
              <p className="text-blue-100">
                Connect with your local representative for personalized service and support.
              </p>
            </div>
            <Link
              to="/representatives"
              data-testid="find-representative-btn"
              className="inline-flex items-center space-x-2 bg-white text-blue-900 font-semibold px-6 py-3 rounded-lg hover:bg-blue-50 transition-colors whitespace-nowrap"
            >
              <span>Find Your Representative</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
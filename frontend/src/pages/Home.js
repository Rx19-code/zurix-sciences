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
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6" data-testid="hero-title">
              Premium Research Compounds
            </h1>
            <p className="text-xl sm:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
              High-purity peptides, GLP-1 analogs, and research chemicals for scientific studies and laboratory research.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/products"
                data-testid="browse-products-btn"
                className="inline-flex items-center space-x-2 bg-white text-blue-900 font-semibold px-8 py-3 rounded-lg hover:bg-blue-50 transition-colors"
              >
                <span>Browse Products</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/verify"
                data-testid="verify-product-btn"
                className="inline-flex items-center space-x-2 bg-blue-700 hover:bg-blue-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
              >
                <span>Verify Product</span>
              </Link>
            </div>
          </div>
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
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Why Choose RX Research Sciences</h2>
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
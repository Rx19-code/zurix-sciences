import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ShoppingCart, Package, Calendar, FileText, Thermometer, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { useCart } from '../context/CartContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`${API}/products/${id}`);
      setProduct(response.data);
    } catch (error) {
      console.error('Error fetching product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    addToCart(product, quantity);
    navigate('/products');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Product not found</h2>
          <button
            onClick={() => navigate('/products')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Back to Products
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="product-detail-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/products')}
          data-testid="back-button"
          className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Products</span>
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Product Image Placeholder */}
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="aspect-square bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center">
              <Package className="w-32 h-32 text-blue-300" />
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-8">
              {/* Category Badge */}
              <span className="inline-block px-3 py-1 bg-blue-50 text-blue-700 text-sm font-semibold rounded-full mb-4">
                {product.category}
              </span>

              <h1 className="text-3xl font-bold text-gray-900 mb-4" data-testid="product-detail-name">
                {product.name}
              </h1>

              <p className="text-gray-600 mb-6">{product.description}</p>

              {/* Specifications */}
              <div className="space-y-3 mb-6">
                <div className="flex items-center justify-between py-3 border-b">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-semibold text-gray-900">{product.product_type}</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b">
                  <span className="text-gray-600">Purity:</span>
                  <span className="font-semibold text-gray-900">{product.purity}</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b">
                  <span className="text-gray-600">Dosage:</span>
                  <span className="font-semibold text-gray-900">{product.dosage}</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b">
                  <span className="text-gray-600">Verification Code:</span>
                  <span className="font-mono text-sm font-semibold text-blue-600" data-testid="verification-code">
                    {product.verification_code}
                  </span>
                </div>
              </div>

              {/* Price and Add to Cart */}
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-600">Price:</span>
                  <span className="text-3xl font-bold text-blue-600" data-testid="product-detail-price">
                    ${product.price.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center space-x-4 mb-4">
                  <span className="text-gray-600">Quantity:</span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      data-testid="decrease-quantity"
                      className="w-10 h-10 flex items-center justify-center bg-white border border-gray-300 rounded hover:bg-gray-50"
                    >
                      -
                    </button>
                    <span className="w-12 text-center font-medium" data-testid="quantity-display">{quantity}</span>
                    <button
                      onClick={() => setQuantity(quantity + 1)}
                      data-testid="increase-quantity"
                      className="w-10 h-10 flex items-center justify-center bg-white border border-gray-300 rounded hover:bg-gray-50"
                    >
                      +
                    </button>
                  </div>
                </div>

                <button
                  onClick={handleAddToCart}
                  data-testid="add-to-cart-button"
                  className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  <ShoppingCart className="w-5 h-5" />
                  <span>Add to Cart</span>
                </button>
              </div>
            </div>

            {/* Product Details Tabs */}
            <div className="bg-white rounded-xl shadow-sm p-8 space-y-6">
              {/* Storage Information */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <Thermometer className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-bold text-gray-900">Storage Information</h3>
                </div>
                <p className="text-gray-600 text-sm" data-testid="storage-info">
                  {product.storage_info}
                </p>
              </div>

              {/* Batch Information */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-bold text-gray-900">Batch Information</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Batch Number:</span>
                    <span className="font-mono font-semibold text-gray-900" data-testid="batch-number">
                      {product.batch_number}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Manufacturing Date:</span>
                    <span className="font-semibold text-gray-900">{product.manufacturing_date}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Expiry Date:</span>
                    <span className="font-semibold text-gray-900">{product.expiry_date}</span>
                  </div>
                </div>
              </div>

              {/* Certificate of Analysis */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-bold text-gray-900">Certificate of Analysis</h3>
                </div>
                <button className="text-blue-600 hover:text-blue-700 font-medium text-sm">
                  Download COA
                </button>
              </div>

              {/* Warning */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-yellow-900 mb-1">For Research Use Only</h4>
                    <p className="text-sm text-yellow-800">
                      This product is intended for laboratory research use only. Not for human or veterinary use.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
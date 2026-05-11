import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Star, FlaskConical } from 'lucide-react';
import { useCart } from '../context/CartContext';

const ProductCard = ({ product }) => {
  const { addToCart } = useCart();
  const isComingSoon = product.coming_soon === true;

  const handleAddToCart = (e) => {
    e.preventDefault();
    if (isComingSoon) return;
    addToCart(product);
  };

  return (
    <Link
      to={`/products/${product.id}`}
      className="group bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-100 relative"
      data-testid={`product-card-${product.id}`}
    >
      {/* Coming Soon Ribbon */}
      {isComingSoon && (
        <div className="absolute top-3 right-3 z-10 bg-amber-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md" data-testid="coming-soon-badge">
          Coming Soon
        </div>
      )}

      {/* Product Image */}
      <div className="h-56 bg-white overflow-hidden flex items-center justify-center p-4">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} className="h-48 w-auto object-contain" />
        ) : (
          <div className="flex flex-col items-center justify-center text-gray-300">
            <FlaskConical className="w-20 h-20" strokeWidth={1.25} />
            {isComingSoon && (
              <span className="mt-2 text-xs text-gray-400 font-medium uppercase tracking-wider">Image Soon</span>
            )}
          </div>
        )}
      </div>

      <div className="p-6">
        {/* Badge */}
        <div className="flex items-center justify-between mb-3">
          <span className="inline-block px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full">
            {product.category}
          </span>
          {product.featured && !isComingSoon && (
            <div className="flex items-center space-x-1 text-yellow-500">
              <Star className="w-4 h-4 fill-current" />
              <span className="text-xs font-semibold">Featured</span>
            </div>
          )}
        </div>

        {/* Product Name */}
        <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors" data-testid="product-name">
          {product.name}
        </h3>

        {/* Product Details */}
        <div className="space-y-1 mb-4">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Type:</span> {product.product_type}
          </p>
          <p className="text-sm text-gray-600">
            <span className="font-medium">Purity:</span> {product.purity}
          </p>
          <p className="text-sm text-gray-600">
            <span className="font-medium">Dosage:</span> {product.dosage}
          </p>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {product.description}
        </p>

        {/* Action */}
        <div className="flex items-center justify-end pt-4 border-t">
          {isComingSoon ? (
            <button
              disabled
              data-testid={`coming-soon-${product.id}`}
              className="flex items-center space-x-2 bg-gray-100 text-gray-500 font-medium px-4 py-2 rounded-lg cursor-not-allowed border border-gray-200"
            >
              <span>Coming Soon</span>
            </button>
          ) : (
            <button
              onClick={handleAddToCart}
              data-testid={`add-to-cart-${product.id}`}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <ShoppingCart className="w-4 h-4" />
              <span>Add to Cart</span>
            </button>
          )}
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;

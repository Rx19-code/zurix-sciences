import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Star } from 'lucide-react';
import { useCart } from '../context/CartContext';

const ProductCard = ({ product }) => {
  const { addToCart } = useCart();

  const handleAddToCart = (e) => {
    e.preventDefault();
    addToCart(product);
  };

  return (
    <Link
      to={`/products/${product.id}`}
      className="group bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-100"
      data-testid={`product-card-${product.id}`}
    >
      {/* Product Image */}
      {product.image_url && (
        <div className="h-56 bg-gradient-to-b from-gray-50 to-gray-100 overflow-hidden flex items-center justify-center p-4">
          <img 
            src={product.image_url} 
            alt={product.name}
            className="h-48 w-auto object-contain drop-shadow-md"
          />
        </div>
      )}
      
      <div className="p-6">
        {/* Badge */}
        <div className="flex items-center justify-between mb-3">
          <span className="inline-block px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full">
            {product.category}
          </span>
          {product.featured && (
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

        {/* Price & Action */}
        <div className="flex items-center justify-between pt-4 border-t">
          <span className="text-2xl font-bold text-blue-600" data-testid="product-price">
            ${product.price.toFixed(2)}
          </span>
          <button
            onClick={handleAddToCart}
            data-testid={`add-to-cart-${product.id}`}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Add to Cart</span>
          </button>
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;
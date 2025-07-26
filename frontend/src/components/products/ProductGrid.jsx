import React from 'react';
import ProductCard from './ProductCard';

const ProductGrid = ({ products, onProductClick, userId }) => {
  if (!products || products.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard
          key={product.product_id}
          product={product}
          onClick={() => onProductClick(product.product_id)}
          userId={userId}
        />
      ))}
    </div>
  );
};

export default ProductGrid;

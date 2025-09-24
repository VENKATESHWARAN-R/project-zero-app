/**
 * ProductCard Component Tests
 * Tests for the product card component that displays product information
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from '@/components/product/ProductCard';
import { Product } from '@/types/product';

const mockProduct: Product = {
  id: 'product-1',
  name: 'Gaming Laptop Pro',
  description: 'High-performance gaming laptop',
  price: 149999,
  currency: 'USD',
  category: 'electronics',
  imageUrl: 'https://example.com/laptop.jpg',
  inStock: true,
  stockQuantity: 15,
  createdAt: '2025-09-24T10:00:00Z',
  updatedAt: '2025-09-24T10:00:00Z',
};

const mockOnAddToCart = jest.fn();
const mockOnViewDetails = jest.fn();

describe('ProductCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render product information correctly', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
    expect(screen.getByText('High-performance gaming laptop')).toBeInTheDocument();
    expect(screen.getByText('$1,499.99')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'Gaming Laptop Pro' })).toBeInTheDocument();
  });

  it('should display in stock status', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('In Stock')).toBeInTheDocument();
  });

  it('should display out of stock status', () => {
    const outOfStockProduct = { ...mockProduct, inStock: false, stockQuantity: 0 };

    render(
      <ProductCard
        product={outOfStockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Out of Stock')).toBeInTheDocument();
  });

  it('should handle add to cart click', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    fireEvent.click(screen.getByText('Add to Cart'));
    expect(mockOnAddToCart).toHaveBeenCalledWith(mockProduct.id);
  });

  it('should disable add to cart button when out of stock', () => {
    const outOfStockProduct = { ...mockProduct, inStock: false, stockQuantity: 0 };

    render(
      <ProductCard
        product={outOfStockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    const addToCartButton = screen.getByText('Out of Stock');
    expect(addToCartButton).toBeDisabled();
  });

  it('should handle view details click', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    fireEvent.click(screen.getByText('View Details'));
    expect(mockOnViewDetails).toHaveBeenCalledWith(mockProduct.id);
  });

  it('should show loading state when adding to cart', () => {
    const { rerender } = render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    rerender(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
        isAddingToCart={true}
      />
    );

    expect(screen.getByText('Adding...')).toBeInTheDocument();
  });

  it('should handle image load error gracefully', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onViewDetails={mockOnViewDetails}
      />
    );

    const image = screen.getByRole('img');
    fireEvent.error(image);

    // Should show placeholder or fallback image
    expect(image).toHaveAttribute('src');
  });
});
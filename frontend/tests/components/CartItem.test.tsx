/**
 * CartItem Component Tests
 * Tests for the cart item component that displays cart item information
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { CartItem } from '@/components/cart/CartItem';
import { CartItem as CartItemType } from '@/types/cart';

const mockCartItem: CartItemType = {
  id: 'cart-item-1',
  productId: 'product-1',
  quantity: 2,
  addedAt: '2025-09-24T10:00:00Z',
  product: {
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
  },
};

const mockOnUpdateQuantity = jest.fn();
const mockOnRemove = jest.fn();

describe('CartItem', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render cart item information correctly', () => {
    render(
      <CartItem
        item={mockCartItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
    expect(screen.getByText('$1,499.99')).toBeInTheDocument();
    expect(screen.getByDisplayValue('2')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'Gaming Laptop Pro' })).toBeInTheDocument();
  });

  it('should calculate and display total price', () => {
    render(
      <CartItem
        item={mockCartItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    expect(screen.getByText('$2,999.98')).toBeInTheDocument(); // 2 × $1,499.99
  });

  it('should handle quantity increase', () => {
    render(
      <CartItem
        item={mockCartItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    fireEvent.click(screen.getByLabelText('Increase quantity'));
    expect(mockOnUpdateQuantity).toHaveBeenCalledWith(mockCartItem.id, 3);
  });

  it('should handle quantity decrease', () => {
    render(
      <CartItem
        item={mockCartItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    fireEvent.click(screen.getByLabelText('Decrease quantity'));
    expect(mockOnUpdateQuantity).toHaveBeenCalledWith(mockCartItem.id, 1);
  });

  it('should handle direct quantity input change', () => {
    render(
      <CartItem
        item={mockCartItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    const quantityInput = screen.getByDisplayValue('2');
    fireEvent.change(quantityInput, { target: { value: '5' } });
    fireEvent.blur(quantityInput);

    expect(mockOnUpdateQuantity).toHaveBeenCalledWith(mockCartItem.id, 5);
  });

  it('should prevent quantity from going below 1', () => {
    const singleItemCart = { ...mockCartItem, quantity: 1 };

    render(
      <CartItem
        item={singleItemCart}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    const decreaseButton = screen.getByLabelText('Decrease quantity');
    expect(decreaseButton).toBeDisabled();
  });

  it('should handle remove item click', () => {
    render(
      <CartItem
        item={mockCartItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    fireEvent.click(screen.getByLabelText('Remove item'));
    expect(mockOnRemove).toHaveBeenCalledWith(mockCartItem.id);
  });

  it('should show loading state when updating', () => {
    render(
      <CartItem
        item={mockCartItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
        isUpdating={true}
      />
    );

    expect(screen.getByTestId('updating-spinner')).toBeInTheDocument();
  });

  it('should show out of stock warning', () => {
    const outOfStockItem = {
      ...mockCartItem,
      product: { ...mockCartItem.product, inStock: false, stockQuantity: 0 },
    };

    render(
      <CartItem
        item={outOfStockItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    expect(screen.getByText('Out of stock')).toBeInTheDocument();
  });

  it('should limit quantity to available stock', () => {
    const limitedStockItem = {
      ...mockCartItem,
      product: { ...mockCartItem.product, stockQuantity: 3 },
    };

    render(
      <CartItem
        item={limitedStockItem}
        onUpdateQuantity={mockOnUpdateQuantity}
        onRemove={mockOnRemove}
      />
    );

    const quantityInput = screen.getByDisplayValue('2');
    fireEvent.change(quantityInput, { target: { value: '10' } });
    fireEvent.blur(quantityInput);

    expect(mockOnUpdateQuantity).toHaveBeenCalledWith(mockCartItem.id, 3);
  });
});
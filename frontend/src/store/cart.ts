/**
 * Cart store using Zustand
 * Manages shopping cart state and actions
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { Cart, CartItem } from '@/types/cart';
import { CartService } from '@/services/cart';
import { useAuthStore } from './auth';

interface CartState {
  // State
  cart: Cart | null;
  optimisticCart: Cart | null; // For optimistic updates
  isLoading: boolean;
  error: string | null;
  lastUpdated: number | null;

  // Actions
  loadCart: () => Promise<void>;
  addItem: (productId: string, quantity: number) => Promise<void>;
  updateItemQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  validateCart: () => Promise<boolean>;
  syncWithStorage: () => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;

  // Optimistic actions
  addItemOptimistic: (productId: string, quantity: number, product: any) => void;
  updateItemQuantityOptimistic: (itemId: string, quantity: number) => void;
  removeItemOptimistic: (itemId: string) => void;
  rollbackOptimistic: () => void;
  commitOptimistic: () => void;
}

export const useCartStore = create<CartState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    cart: null,
    optimisticCart: null,
    isLoading: false,
    error: null,
    lastUpdated: null,

    // Actions
    loadCart: async () => {
      const authStore = useAuthStore.getState();

      // Only load cart if user is authenticated
      if (!authStore.isAuthenticated) {
        set({
          cart: null,
          error: null,
        });
        return;
      }

      set({ isLoading: true, error: null });

      try {
        const cartData = await CartService.getCart();
        const transformedCart = CartService.transformCartFromApi(cartData);

        // Save to local storage
        CartService.saveCartToStorage(transformedCart, authStore.user?.id);

        set({
          cart: transformedCart,
          optimisticCart: null, // Clear optimistic state
          isLoading: false,
          error: null,
          lastUpdated: Date.now(),
        });
      } catch (error: any) {
        // Try to load from storage if API fails
        const authStore = useAuthStore.getState();
        const storedCart = CartService.loadCartFromStorage(authStore.user?.id);

        set({
          cart: storedCart,
          isLoading: false,
          error: error.detail || error.message || 'Failed to load cart',
          lastUpdated: storedCart ? Date.now() : null,
        });
      }
    },

    addItem: async (productId: string, quantity: number) => {
      const authStore = useAuthStore.getState();

      if (!authStore.isAuthenticated) {
        set({ error: 'Please login to add items to cart' });
        return;
      }

      set({ error: null });

      try {
        await CartService.addToCart(productId, quantity);

        // Reload cart to get updated totals
        await get().loadCart();

        // Commit optimistic changes if they exist
        get().commitOptimistic();

      } catch (error: any) {
        // Rollback optimistic changes on error
        get().rollbackOptimistic();

        set({
          error: error.detail || error.message || 'Failed to add item to cart',
        });
        throw error;
      }
    },

    updateItemQuantity: async (itemId: string, quantity: number) => {
      if (quantity <= 0) {
        await get().removeItem(itemId);
        return;
      }

      set({ error: null });

      try {
        await CartService.updateCartItem(itemId, quantity);

        // Reload cart to get updated totals
        await get().loadCart();

        // Commit optimistic changes if they exist
        get().commitOptimistic();

      } catch (error: any) {
        // Rollback optimistic changes on error
        get().rollbackOptimistic();

        set({
          error: error.detail || error.message || 'Failed to update item quantity',
        });
        throw error;
      }
    },

    removeItem: async (itemId: string) => {
      set({ error: null });

      try {
        await CartService.removeFromCart(itemId);

        // Reload cart to get updated state
        await get().loadCart();

        // Commit optimistic changes if they exist
        get().commitOptimistic();

      } catch (error: any) {
        // Rollback optimistic changes on error
        get().rollbackOptimistic();

        set({
          error: error.detail || error.message || 'Failed to remove item',
        });
        throw error;
      }
    },

    clearCart: async () => {
      set({ isLoading: true, error: null });

      try {
        await CartService.clearCart();

        const authStore = useAuthStore.getState();
        CartService.clearCartFromStorage(authStore.user?.id);

        set({
          cart: null,
          isLoading: false,
          error: null,
          lastUpdated: Date.now(),
        });

      } catch (error: any) {
        set({
          isLoading: false,
          error: error.detail || error.message || 'Failed to clear cart',
        });
        throw error;
      }
    },

    validateCart: async () => {
      const cart = get().cart;

      if (!cart || CartService.isEmpty(cart)) {
        return true;
      }

      try {
        const validation = await CartService.validateCart();

        if (!validation.valid) {
          set({
            error: `Cart validation failed: ${validation.issues.map(issue => issue.message).join(', ')}`,
          });

          // Reload cart to get updated state
          await get().loadCart();

          return false;
        }

        return true;
      } catch (error: any) {
        set({
          error: error.detail || error.message || 'Failed to validate cart',
        });
        return false;
      }
    },

    syncWithStorage: () => {
      try {
        const authStore = useAuthStore.getState();
        const cart = get().cart;

        if (cart && authStore.user?.id) {
          CartService.saveCartToStorage(cart, authStore.user.id);
        }
      } catch (error) {
        console.error('Failed to sync cart with storage:', error);
      }
    },

    clearError: () => {
      set({ error: null });
    },

    setLoading: (loading: boolean) => {
      set({ isLoading: loading });
    },

    // Optimistic actions
    addItemOptimistic: (productId: string, quantity: number, product: any) => {
      const currentCart = get().optimisticCart || get().cart;

      if (!currentCart) return;

      const newItem: CartItem = {
        id: `temp-${productId}-${Date.now()}`,
        productId,
        quantity,
        addedAt: new Date().toISOString(),
        product: {
          id: product.id,
          name: product.name,
          price: product.price,
          currency: product.currency,
          imageUrl: product.imageUrl,
          inStock: product.inStock,
          stockQuantity: product.stockQuantity,
        },
      };

      // Check if item already exists
      const existingItemIndex = currentCart.items.findIndex(
        item => item.productId === productId
      );

      let newItems: CartItem[];
      if (existingItemIndex >= 0) {
        // Update existing item
        newItems = [...currentCart.items];
        newItems[existingItemIndex] = {
          ...newItems[existingItemIndex],
          quantity: newItems[existingItemIndex].quantity + quantity,
        };
      } else {
        // Add new item
        newItems = [...currentCart.items, newItem];
      }

      const newTotal = CartService.calculateTotal(newItems);
      const newItemCount = CartService.calculateItemCount(newItems);

      const optimisticCart: Cart = {
        ...currentCart,
        items: newItems,
        totalAmount: newTotal,
        itemCount: newItemCount,
        updatedAt: new Date().toISOString(),
      };

      set({ optimisticCart });
    },

    updateItemQuantityOptimistic: (itemId: string, newQuantity: number) => {
      const currentCart = get().optimisticCart || get().cart;

      if (!currentCart) return;

      const newItems = currentCart.items.map(item =>
        item.id === itemId ? { ...item, quantity: newQuantity } : item
      );

      const newTotal = CartService.calculateTotal(newItems);
      const newItemCount = CartService.calculateItemCount(newItems);

      const optimisticCart: Cart = {
        ...currentCart,
        items: newItems,
        totalAmount: newTotal,
        itemCount: newItemCount,
        updatedAt: new Date().toISOString(),
      };

      set({ optimisticCart });
    },

    removeItemOptimistic: (itemId: string) => {
      const currentCart = get().optimisticCart || get().cart;

      if (!currentCart) return;

      const newItems = currentCart.items.filter(item => item.id !== itemId);
      const newTotal = CartService.calculateTotal(newItems);
      const newItemCount = CartService.calculateItemCount(newItems);

      const optimisticCart: Cart = {
        ...currentCart,
        items: newItems,
        totalAmount: newTotal,
        itemCount: newItemCount,
        updatedAt: new Date().toISOString(),
      };

      set({ optimisticCart });
    },

    rollbackOptimistic: () => {
      set({ optimisticCart: null });
    },

    commitOptimistic: () => {
      const { optimisticCart } = get();
      if (optimisticCart) {
        set({ cart: optimisticCart, optimisticCart: null });
      }
    },
  }))
);

// Auto-save cart to storage when it changes
if (typeof window !== 'undefined') {
  useCartStore.subscribe(
    (state) => state.cart,
    (cart) => {
      if (cart) {
        const authStore = useAuthStore.getState();
        if (authStore.user?.id) {
          CartService.saveCartToStorage(cart, authStore.user.id);
        }
      }
    }
  );

  // Load cart when user authentication state changes
  useAuthStore.subscribe(
    (state) => state.isAuthenticated,
    (isAuthenticated) => {
      if (isAuthenticated) {
        // User logged in, load their cart
        useCartStore.getState().loadCart();
      } else {
        // User logged out, clear cart
        useCartStore.setState({
          cart: null,
          error: null,
        });
      }
    }
  );
}

// Computed values and selectors
export const useCartSelectors = () => {
  const cart = useCartStore(state => state.cart);
  const optimisticCart = useCartStore(state => state.optimisticCart);
  const isLoading = useCartStore(state => state.isLoading);
  const error = useCartStore(state => state.error);

  // Use optimistic cart if available, otherwise use regular cart
  const displayCart = optimisticCart || cart;

  return {
    cart: displayCart,
    isLoading,
    error,
    itemCount: displayCart ? CartService.calculateItemCount(displayCart.items) : 0,
    totalAmount: displayCart ? CartService.calculateTotal(displayCart.items) : 0,
    formattedTotal: displayCart ? CartService.formatCartTotal(CartService.calculateTotal(displayCart.items), displayCart.currency) : '$0.00',
    isEmpty: displayCart ? CartService.isEmpty(displayCart) : true,
    hasValidStock: displayCart ? CartService.hasValidStock(displayCart) : true,
    itemsWithInsufficientStock: displayCart ? CartService.getItemsWithInsufficientStock(displayCart) : [],
    isOptimistic: !!optimisticCart,
  };
};

// Hook for cart actions
export const useCartActions = () => {
  const {
    loadCart,
    addItem,
    updateItemQuantity,
    removeItem,
    clearCart,
    validateCart,
    clearError,
    addItemOptimistic,
    updateItemQuantityOptimistic,
    removeItemOptimistic,
    rollbackOptimistic,
    commitOptimistic,
  } = useCartStore();

  return {
    loadCart,
    addItem,
    updateItemQuantity,
    removeItem,
    clearCart,
    validateCart,
    clearError,
    addItemOptimistic,
    updateItemQuantityOptimistic,
    removeItemOptimistic,
    rollbackOptimistic,
    commitOptimistic,
  };
};

export default useCartStore;
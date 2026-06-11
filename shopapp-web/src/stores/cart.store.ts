import { create } from "zustand";
import type { CartResponse } from "@/types";
import api from "@/lib/api";

interface CartState {
  cart: CartResponse | null;
  isLoading: boolean;
  fetchCart: () => Promise<void>;
  addItem: (variantId: number, quantity?: number) => Promise<void>;
  updateItem: (itemId: number, quantity: number) => Promise<void>;
  removeItem: (itemId: number) => Promise<void>;
  clearCart: () => Promise<void>;
}

export const useCartStore = create<CartState>((set) => ({
  cart: null,
  isLoading: false,

  fetchCart: async () => {
    set({ isLoading: true });
    try {
      const { data } = await api.get("/cart");
      set({ cart: data });
    } catch {
      set({ cart: null });
    } finally {
      set({ isLoading: false });
    }
  },

  addItem: async (variantId, quantity = 1) => {
    await api.post("/cart", { variant_id: variantId, quantity });
    const { data } = await api.get("/cart");
    set({ cart: data });
  },

  updateItem: async (itemId, quantity) => {
    await api.put(`/cart/${itemId}`, { quantity });
    const { data } = await api.get("/cart");
    set({ cart: data });
  },

  removeItem: async (itemId) => {
    await api.delete(`/cart/${itemId}`);
    const { data } = await api.get("/cart");
    set({ cart: data });
  },

  clearCart: async () => {
    await api.delete("/cart");
    set({ cart: null });
  },
}));

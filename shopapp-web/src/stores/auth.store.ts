import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";
import api from "@/lib/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const { data } = await api.post("/auth/login", { email, password });
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          const me = await api.get("/auth/me");
          set({ user: me.data });
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (email, fullName, password) => {
        set({ isLoading: true });
        try {
          const { data } = await api.post("/auth/register", {
            email, full_name: fullName, password,
          });
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          const me = await api.get("/auth/me");
          set({ user: me.data });
        } finally {
          set({ isLoading: false });
        }
      },

      logout: () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        set({ user: null });
      },

      fetchMe: async () => {
        try {
          const { data } = await api.get("/auth/me");
          set({ user: data });
        } catch {
          set({ user: null });
        }
      },
    }),
    { name: "auth-store", partialize: (s) => ({ user: s.user }) }
  )
);

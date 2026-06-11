"use client";
import Link from "next/link";
import { ShoppingCart, User, Menu, Search, Package } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth.store";
import { useCartStore } from "@/stores/cart.store";
import { useEffect, useState } from "react";

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const { cart, fetchCart } = useCartStore();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (user) fetchCart();
  }, [user]);

  const cartCount = cart?.total_items ?? 0;

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <Package className="h-6 w-6 text-primary" />
          ShopApp
        </Link>

        {/* Search - desktop */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Tìm kiếm sản phẩm..."
              className="w-full rounded-full border bg-muted pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Cart */}
          <Link href="/cart">
            <Button variant="ghost" size="icon" className="relative">
              <ShoppingCart className="h-5 w-5" />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-bold">
                  {cartCount > 9 ? "9+" : cartCount}
                </span>
              )}
            </Button>
          </Link>

          {/* Auth */}
          {user ? (
            <div className="relative">
              <Button variant="ghost" size="icon" onClick={() => setMenuOpen(!menuOpen)}>
                <User className="h-5 w-5" />
              </Button>
              {menuOpen && (
                <div className="absolute right-0 top-12 w-48 rounded-lg border bg-background shadow-lg z-50">
                  <div className="p-3 border-b">
                    <p className="font-medium text-sm truncate">{user.full_name}</p>
                    <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                  </div>
                  <div className="p-1">
                    <Link href="/orders" onClick={() => setMenuOpen(false)}>
                      <button className="w-full text-left px-3 py-2 text-sm hover:bg-muted rounded-md">Đơn hàng</button>
                    </Link>
                    {user.role === "admin" && (
                      <Link href="/admin" onClick={() => setMenuOpen(false)}>
                        <button className="w-full text-left px-3 py-2 text-sm hover:bg-muted rounded-md">Admin</button>
                      </Link>
                    )}
                    <button
                      onClick={() => { logout(); setMenuOpen(false); }}
                      className="w-full text-left px-3 py-2 text-sm text-destructive hover:bg-muted rounded-md"
                    >
                      Đăng xuất
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link href="/login">
              <Button size="sm">Đăng nhập</Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

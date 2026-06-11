"use client";
import { useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { Minus, Plus, Trash2, ShoppingBag, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/index";
import { formatPrice } from "@/lib/utils";
import { useCartStore } from "@/stores/cart.store";
import { useAuthStore } from "@/stores/auth.store";
import { toast } from "sonner";

export default function CartPage() {
  const { cart, fetchCart, updateItem, removeItem, isLoading } = useCartStore();
  const { user } = useAuthStore();

  useEffect(() => {
    if (user) fetchCart();
  }, [user]);

  if (!user) return (
    <div className="text-center py-20 space-y-4">
      <ShoppingBag className="h-16 w-16 mx-auto text-muted-foreground" />
      <p className="text-muted-foreground">Vui lòng đăng nhập để xem giỏ hàng</p>
      <Link href="/login"><Button>Đăng nhập</Button></Link>
    </div>
  );

  if (isLoading) return (
    <div className="flex justify-center py-20">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );

  if (!cart?.items.length) return (
    <div className="text-center py-20 space-y-4">
      <ShoppingBag className="h-16 w-16 mx-auto text-muted-foreground" />
      <p className="text-muted-foreground">Giỏ hàng trống</p>
      <Link href="/"><Button>Tiếp tục mua sắm</Button></Link>
    </div>
  );

  const shippingFee = cart.subtotal >= 500000 ? 0 : 30000;
  const total = cart.subtotal + shippingFee;

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Giỏ hàng ({cart.total_items} sản phẩm)</h1>
      <div className="grid md:grid-cols-3 gap-6">
        {/* Items */}
        <div className="md:col-span-2 space-y-3">
          {cart.items.map((item) => (
            <div key={item.id} className="flex gap-4 rounded-xl border p-4 bg-card">
              <div className="relative h-20 w-20 flex-shrink-0 rounded-lg overflow-hidden bg-muted">
                <div className="absolute inset-0 flex items-center justify-center text-xs text-muted-foreground">
                  Ảnh
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm line-clamp-1">{item.variant.name}</p>
                <p className="text-xs text-muted-foreground">SKU: {item.variant.sku}</p>
                <p className="text-primary font-bold mt-1">{formatPrice(item.variant.price)}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <button
                  onClick={async () => {
                    await removeItem(item.id);
                    toast.success("Đã xóa khỏi giỏ hàng");
                  }}
                  className="text-muted-foreground hover:text-destructive transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                <div className="flex items-center border rounded-lg">
                  <button
                    onClick={() => updateItem(item.id, Math.max(1, item.quantity - 1))}
                    className="px-2 py-1 hover:bg-muted transition-colors"
                  >
                    <Minus className="h-3 w-3" />
                  </button>
                  <span className="px-3 py-1 text-sm font-medium">{item.quantity}</span>
                  <button
                    onClick={() => updateItem(item.id, item.quantity + 1)}
                    className="px-2 py-1 hover:bg-muted transition-colors"
                  >
                    <Plus className="h-3 w-3" />
                  </button>
                </div>
                <p className="text-sm font-bold">{formatPrice(item.variant.price * item.quantity)}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="rounded-xl border p-5 bg-card h-fit space-y-4 sticky top-20">
          <h2 className="font-bold text-lg">Tóm tắt đơn hàng</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Tạm tính</span>
              <span>{formatPrice(cart.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Phí vận chuyển</span>
              <span>{shippingFee === 0 ? <span className="text-green-600">Miễn phí</span> : formatPrice(shippingFee)}</span>
            </div>
            {shippingFee > 0 && (
              <p className="text-xs text-muted-foreground">Miễn phí ship cho đơn từ {formatPrice(500000)}</p>
            )}
          </div>
          <Separator />
          <div className="flex justify-between font-bold text-lg">
            <span>Tổng cộng</span>
            <span className="text-primary">{formatPrice(total)}</span>
          </div>
          <Link href="/checkout">
            <Button className="w-full" size="lg">Tiến hành thanh toán</Button>
          </Link>
          <Link href="/">
            <Button variant="outline" className="w-full">Tiếp tục mua sắm</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

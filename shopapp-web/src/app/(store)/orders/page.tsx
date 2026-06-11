"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Package, Loader2 } from "lucide-react";
import api from "@/lib/api";
import type { PaginatedResponse, Order } from "@/types";
import { Button } from "@/components/ui/button";
import { formatPrice, formatDate, ORDER_STATUS_LABEL, ORDER_STATUS_COLOR } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth.store";

export default function OrdersPage() {
  const { user } = useAuthStore();

  const { data, isLoading } = useQuery<PaginatedResponse<Order>>({
    queryKey: ["my-orders"],
    queryFn: async () => (await api.get("/orders/my?size=20")).data,
    enabled: !!user,
  });

  if (!user) return (
    <div className="text-center py-20 space-y-4">
      <p className="text-muted-foreground">Vui lòng đăng nhập</p>
      <Link href="/login"><Button>Đăng nhập</Button></Link>
    </div>
  );

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Đơn hàng của tôi</h1>
      {!data?.items.length ? (
        <div className="text-center py-20 space-y-4">
          <Package className="h-16 w-16 mx-auto text-muted-foreground" />
          <p className="text-muted-foreground">Bạn chưa có đơn hàng nào</p>
          <Link href="/"><Button>Mua sắm ngay</Button></Link>
        </div>
      ) : (
        <div className="space-y-4">
          {data.items.map((order) => (
            <div key={order.id} className="rounded-xl border bg-card p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-bold">#{order.order_code}</p>
                  <p className="text-xs text-muted-foreground">{formatDate(order.created_at)}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${ORDER_STATUS_COLOR[order.status]}`}>
                  {ORDER_STATUS_LABEL[order.status]}
                </span>
              </div>
              <div className="space-y-1">
                {order.items.map((item) => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{item.product_name} × {item.quantity}</span>
                    <span>{formatPrice(item.subtotal)}</span>
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-between pt-2 border-t">
                <span className="text-sm text-muted-foreground">Tổng cộng</span>
                <span className="font-bold text-primary">{formatPrice(order.total)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

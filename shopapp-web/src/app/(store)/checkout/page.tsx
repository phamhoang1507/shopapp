"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Loader2, CheckCircle } from "lucide-react";
import api from "@/lib/api";
import type { Address } from "@/types";
import { Button } from "@/components/ui/button";
import { Input, Label, Card, CardContent, CardHeader, CardTitle, Separator } from "@/components/ui/index";
import { formatPrice } from "@/lib/utils";
import { useCartStore } from "@/stores/cart.store";
import { useAuthStore } from "@/stores/auth.store";
import { toast } from "sonner";

export default function CheckoutPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { cart, fetchCart } = useCartStore();
  const [paymentMethod, setPaymentMethod] = useState("cod");
  const [note, setNote] = useState("");
  const [placing, setPlacing] = useState(false);
  const [useNewAddress, setUseNewAddress] = useState(false);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null);
  const [newAddress, setNewAddress] = useState({
    full_name: user?.full_name ?? "",
    phone: user?.phone ?? "",
    province: "", district: "", ward: "", street: "", is_default: false,
  });

  const { data: addresses } = useQuery<Address[]>({
    queryKey: ["addresses"],
    queryFn: async () => (await api.get("/users/me/addresses")).data,
    enabled: !!user,
  });

  // Thay onSuccess bằng useEffect
  useEffect(() => {
    if (!addresses) return;
    const def = addresses.find((a) => a.is_default) ?? addresses[0];
    if (def) setSelectedAddressId(def.id);
    if (!addresses.length) setUseNewAddress(true);
  }, [addresses]);

  const shippingFee = (cart?.subtotal ?? 0) >= 500000 ? 0 : 30000;
  const total = (cart?.subtotal ?? 0) + shippingFee;

  const handlePlaceOrder = async () => {
    let addressId = selectedAddressId;

    if (useNewAddress || !addressId) {
      if (!newAddress.phone || !newAddress.province || !newAddress.street) {
        toast.error("Vui lòng điền đầy đủ địa chỉ");
        return;
      }
      const { data } = await api.post("/users/me/addresses", {
        ...newAddress,
        ward: newAddress.ward || "N/A",
        district: newAddress.district || "N/A",
      });
      addressId = data.id;
    }

    setPlacing(true);
    try {
      await api.post("/orders", {
        address_id: addressId,
        payment_method: paymentMethod,
        note: note || undefined,
      });
      await fetchCart();
      toast.success("Đặt hàng thành công!");
      router.push("/orders");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Đặt hàng thất bại");
    } finally {
      setPlacing(false);
    }
  };

  if (!user) { router.push("/login"); return null; }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Thanh toán</h1>
      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-5">
          {/* Shipping address */}
          <Card>
            <CardHeader><CardTitle className="text-base">Địa chỉ giao hàng</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {addresses && addresses.length > 0 && !useNewAddress ? (
                <>
                  {addresses.map((addr) => (
                    <label key={addr.id} className={`flex gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${selectedAddressId === addr.id ? "border-primary bg-primary/5" : "hover:bg-muted"}`}>
                      <input type="radio" name="address" checked={selectedAddressId === addr.id} onChange={() => setSelectedAddressId(addr.id)} className="mt-1" />
                      <div className="text-sm">
                        <p className="font-medium">{addr.full_name} • {addr.phone}</p>
                        <p className="text-muted-foreground">{addr.street}, {addr.ward}, {addr.district}, {addr.province}</p>
                      </div>
                    </label>
                  ))}
                  <Button variant="outline" size="sm" onClick={() => setUseNewAddress(true)}>+ Địa chỉ mới</Button>
                </>
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1"><Label>Họ tên</Label><Input value={newAddress.full_name} onChange={(e) => setNewAddress({...newAddress, full_name: e.target.value})} /></div>
                  <div className="space-y-1"><Label>Số điện thoại</Label><Input value={newAddress.phone} onChange={(e) => setNewAddress({...newAddress, phone: e.target.value})} /></div>
                  <div className="space-y-1"><Label>Tỉnh/Thành phố</Label><Input value={newAddress.province} onChange={(e) => setNewAddress({...newAddress, province: e.target.value})} /></div>
                  <div className="space-y-1"><Label>Quận/Huyện</Label><Input value={newAddress.district} onChange={(e) => setNewAddress({...newAddress, district: e.target.value})} /></div>
                  <div className="space-y-1"><Label>Phường/Xã</Label><Input value={newAddress.ward} onChange={(e) => setNewAddress({...newAddress, ward: e.target.value})} /></div>
                  <div className="space-y-1"><Label>Số nhà, tên đường</Label><Input value={newAddress.street} onChange={(e) => setNewAddress({...newAddress, street: e.target.value})} /></div>
                  {addresses && addresses.length > 0 && (
                    <Button variant="ghost" size="sm" onClick={() => setUseNewAddress(false)} className="col-span-2">← Dùng địa chỉ đã lưu</Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Payment method */}
          <Card>
            <CardHeader><CardTitle className="text-base">Phương thức thanh toán</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {[
                { id: "cod", label: "💵 Thanh toán khi nhận hàng (COD)" },
                { id: "bank_transfer", label: "🏦 Chuyển khoản ngân hàng" },
              ].map((method) => (
                <label key={method.id} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${paymentMethod === method.id ? "border-primary bg-primary/5" : "hover:bg-muted"}`}>
                  <input type="radio" name="payment" value={method.id} checked={paymentMethod === method.id} onChange={() => setPaymentMethod(method.id)} />
                  <span className="text-sm font-medium">{method.label}</span>
                </label>
              ))}
            </CardContent>
          </Card>

          {/* Note */}
          <Card>
            <CardHeader><CardTitle className="text-base">Ghi chú đơn hàng</CardTitle></CardHeader>
            <CardContent>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Ghi chú cho người bán (tuỳ chọn)..."
                className="w-full rounded-md border bg-background px-3 py-2 text-sm min-h-[80px] focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              />
            </CardContent>
          </Card>
        </div>

        {/* Summary */}
        <div className="rounded-xl border p-5 bg-card h-fit space-y-4 sticky top-20">
          <h2 className="font-bold">Tóm tắt đơn hàng</h2>
          <div className="space-y-2 text-sm max-h-40 overflow-y-auto">
            {cart?.items.map((item) => (
              <div key={item.id} className="flex justify-between">
                <span className="text-muted-foreground line-clamp-1 flex-1 mr-2">{item.variant.name} ×{item.quantity}</span>
                <span className="flex-shrink-0">{formatPrice(item.variant.price * item.quantity)}</span>
              </div>
            ))}
          </div>
          <Separator />
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Tạm tính</span>
              <span>{formatPrice(cart?.subtotal ?? 0)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Phí ship</span>
              <span>{shippingFee === 0 ? <span className="text-green-600">Miễn phí</span> : formatPrice(shippingFee)}</span>
            </div>
          </div>
          <Separator />
          <div className="flex justify-between font-bold text-lg">
            <span>Tổng cộng</span>
            <span className="text-primary">{formatPrice(total)}</span>
          </div>
          <Button className="w-full gap-2" size="lg" onClick={handlePlaceOrder} disabled={placing || !cart?.items.length}>
            {placing ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
            Đặt hàng
          </Button>
        </div>
      </div>
    </div>
  );
}

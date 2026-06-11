"use client";
import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import Image from "next/image";
import { useParams, useRouter } from "next/navigation";
import { ShoppingCart, Star, Minus, Plus, Loader2 } from "lucide-react";
import api from "@/lib/api";
import type { Product, ProductVariant } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge, Separator } from "@/components/ui/index";
import { formatPrice } from "@/lib/utils";
import { useCartStore } from "@/stores/cart.store";
import { useAuthStore } from "@/stores/auth.store";
import { toast } from "sonner";

export default function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const { addItem } = useCartStore();
  const { user } = useAuthStore();
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [adding, setAdding] = useState(false);

  const { data: product, isLoading } = useQuery<Product>({
    queryKey: ["product", slug],
    queryFn: async () => (await api.get(`/products/slug/${slug}`)).data,
  });

  // Thay onSuccess bằng useEffect
  useEffect(() => {
    if (!product) return;
    const first = product.variants.find((v) => v.is_active && v.stock > 0);
    if (first) setSelectedVariant(first);
  }, [product]);

  const handleAddToCart = async () => {
    if (!user) { router.push("/login"); return; }
    if (!selectedVariant) { toast.error("Vui lòng chọn phân loại"); return; }
    if (selectedVariant.stock < quantity) { toast.error("Không đủ hàng"); return; }
    setAdding(true);
    try {
      await addItem(selectedVariant.id, quantity);
      toast.success("Đã thêm vào giỏ hàng!");
    } catch {
      toast.error("Không thể thêm vào giỏ");
    } finally {
      setAdding(false);
    }
  };

  if (isLoading) return (
    <div className="flex justify-center py-20">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
  if (!product) return <div className="text-center py-20">Không tìm thấy sản phẩm</div>;

  const images = product.images.sort((a, b) => (b.is_primary ? 1 : 0) - (a.is_primary ? 1 : 0));
  const activeVariant = selectedVariant ?? product.variants[0];
  const hasDiscount = activeVariant?.compare_price && activeVariant.compare_price > activeVariant.price;

  return (
    <div className="max-w-5xl mx-auto">
      <div className="grid md:grid-cols-2 gap-8">
        {/* Images */}
        <div className="space-y-3">
          <div className="relative aspect-square rounded-xl overflow-hidden bg-muted">
            {images[selectedImage] ? (
              <Image src={images[selectedImage].url} alt={product.name} fill className="object-cover" sizes="(max-width: 768px) 100vw, 50vw" />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">Chưa có ảnh</div>
            )}
          </div>
          {images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-1">
              {images.map((img, i) => (
                <button key={img.id} onClick={() => setSelectedImage(i)}
                  className={`relative h-16 w-16 flex-shrink-0 rounded-lg overflow-hidden border-2 transition-colors ${i === selectedImage ? "border-primary" : "border-transparent"}`}>
                  <Image src={img.url} alt="" fill className="object-cover" sizes="64px" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="space-y-5">
          {product.category && <p className="text-sm text-muted-foreground">{product.category.name}</p>}
          <h1 className="text-2xl font-bold">{product.name}</h1>

          {product.avg_rating && (
            <div className="flex items-center gap-2">
              <div className="flex">
                {[1,2,3,4,5].map((s) => (
                  <Star key={s} className={`h-4 w-4 ${s <= Math.round(product.avg_rating!) ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground"}`} />
                ))}
              </div>
              <span className="text-sm text-muted-foreground">{product.review_count} đánh giá</span>
            </div>
          )}

          <div className="flex items-center gap-3">
            <span className="text-3xl font-bold text-primary">
              {activeVariant ? formatPrice(activeVariant.price) : "Liên hệ"}
            </span>
            {hasDiscount && <span className="text-lg text-muted-foreground line-through">{formatPrice(activeVariant.compare_price!)}</span>}
            {hasDiscount && (
              <Badge className="bg-red-500 text-white border-0">
                -{Math.round((1 - activeVariant.price / activeVariant.compare_price!) * 100)}%
              </Badge>
            )}
          </div>

          <Separator />

          {product.variants.length > 1 && (
            <div>
              <p className="text-sm font-medium mb-2">Phân loại:</p>
              <div className="flex gap-2 flex-wrap">
                {product.variants.map((v) => (
                  <button key={v.id} onClick={() => v.stock > 0 && setSelectedVariant(v)} disabled={v.stock === 0}
                    className={`px-3 py-1.5 rounded-lg border text-sm transition-colors ${
                      selectedVariant?.id === v.id ? "border-primary bg-primary/10 text-primary font-medium"
                      : v.stock === 0 ? "border-muted text-muted-foreground opacity-50 cursor-not-allowed line-through"
                      : "border-border hover:border-primary"}`}>
                    {v.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div>
            <p className="text-sm font-medium mb-2">Số lượng: <span className="text-muted-foreground font-normal">({activeVariant?.stock ?? 0} sản phẩm)</span></p>
            <div className="flex items-center border rounded-lg w-fit">
              <button onClick={() => setQuantity(q => Math.max(1, q - 1))} className="px-3 py-2 hover:bg-muted transition-colors"><Minus className="h-4 w-4" /></button>
              <span className="px-4 py-2 font-medium min-w-[3rem] text-center">{quantity}</span>
              <button onClick={() => setQuantity(q => Math.min(activeVariant?.stock ?? 1, q + 1))} className="px-3 py-2 hover:bg-muted transition-colors"><Plus className="h-4 w-4" /></button>
            </div>
          </div>

          <Button size="lg" className="w-full gap-2" onClick={handleAddToCart} disabled={adding || !activeVariant || activeVariant.stock === 0}>
            {adding ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShoppingCart className="h-4 w-4" />}
            {activeVariant?.stock === 0 ? "Hết hàng" : "Thêm vào giỏ hàng"}
          </Button>

          {product.description && (
            <>
              <Separator />
              <div>
                <p className="font-medium mb-2">Mô tả sản phẩm</p>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{product.description}</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

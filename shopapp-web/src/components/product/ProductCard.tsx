"use client";
import Image from "next/image";
import Link from "next/link";
import { ShoppingCart, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/index";
import { formatPrice } from "@/lib/utils";
import { useCartStore } from "@/stores/cart.store";
import { useAuthStore } from "@/stores/auth.store";
import type { Product } from "@/types";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const { addItem } = useCartStore();
  const { user } = useAuthStore();
  const router = useRouter();

  const primaryImage = product.images.find((i) => i.is_primary) ?? product.images[0];
  const defaultVariant = product.variants.find((v) => v.is_active && v.stock > 0) ?? product.variants[0];
  const hasDiscount = defaultVariant?.compare_price && defaultVariant.compare_price > defaultVariant.price;
  const discountPct = hasDiscount
    ? Math.round((1 - defaultVariant.price / defaultVariant.compare_price!) * 100)
    : 0;

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!user) { router.push("/login"); return; }
    if (!defaultVariant) return;
    try {
      await addItem(defaultVariant.id, 1);
      toast.success("Đã thêm vào giỏ hàng!");
    } catch {
      toast.error("Không thể thêm vào giỏ");
    }
  };

  return (
    <Link href={`/products/${product.slug}`}>
      <div className="group relative rounded-xl border bg-card hover:shadow-lg transition-all duration-300 overflow-hidden">
        {/* Image */}
        <div className="relative aspect-square overflow-hidden bg-muted">
          {primaryImage ? (
            <Image
              src={primaryImage.url}
              alt={primaryImage.alt_text ?? product.name}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              sizes="(max-width: 768px) 50vw, 25vw"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-muted-foreground text-sm">
              Chưa có ảnh
            </div>
          )}
          {hasDiscount && (
            <Badge className="absolute top-2 left-2 bg-red-500 text-white border-0">
              -{discountPct}%
            </Badge>
          )}
          {/* Quick add button */}
          <button
            onClick={handleAddToCart}
            className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-primary text-primary-foreground rounded-full p-2 shadow-lg hover:bg-primary/90"
          >
            <ShoppingCart className="h-4 w-4" />
          </button>
        </div>

        {/* Info */}
        <div className="p-3">
          {product.category && (
            <p className="text-xs text-muted-foreground mb-1">{product.category.name}</p>
          )}
          <h3 className="font-medium text-sm line-clamp-2 mb-2">{product.name}</h3>

          {/* Rating */}
          {product.avg_rating && (
            <div className="flex items-center gap-1 mb-2">
              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
              <span className="text-xs text-muted-foreground">
                {product.avg_rating.toFixed(1)} ({product.review_count})
              </span>
            </div>
          )}

          {/* Price */}
          <div className="flex items-center gap-2">
            <span className="font-bold text-primary">
              {defaultVariant ? formatPrice(defaultVariant.price) : "Liên hệ"}
            </span>
            {hasDiscount && (
              <span className="text-xs text-muted-foreground line-through">
                {formatPrice(defaultVariant.compare_price!)}
              </span>
            )}
          </div>

          {/* Stock */}
          {defaultVariant && defaultVariant.stock === 0 && (
            <p className="text-xs text-destructive mt-1">Hết hàng</p>
          )}
        </div>
      </div>
    </Link>
  );
}

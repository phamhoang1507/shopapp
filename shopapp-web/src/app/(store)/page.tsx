"use client";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import api from "@/lib/api";
import type { PaginatedResponse, Product, Category } from "@/types";
import ProductCard from "@/components/product/ProductCard";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export default function HomePage() {
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [page, setPage] = useState(1);

  const { data: categories } = useQuery<Category[]>({
    queryKey: ["categories"],
    queryFn: async () => (await api.get("/categories")).data,
  });

  const { data: productsData, isLoading } = useQuery<PaginatedResponse<Product>>({
    queryKey: ["products", selectedCategory, page],
    queryFn: async () => {
      const params = new URLSearchParams({ page: String(page), size: "12" });
      if (selectedCategory) params.set("category_id", String(selectedCategory));
      return (await api.get(`/products?${params}`)).data;
    },
  });

  return (
    <div className="space-y-8">
      {/* Hero banner */}
      <div className="rounded-2xl bg-gradient-to-r from-primary to-blue-600 p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Mua sắm thời trang</h1>
        <p className="text-blue-100 mb-4">Khám phá hàng ngàn sản phẩm chất lượng cao</p>
        <Button variant="secondary" size="lg">Xem ngay</Button>
      </div>

      {/* Category filter */}
      {categories && categories.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={selectedCategory === null ? "default" : "outline"}
            size="sm"
            onClick={() => { setSelectedCategory(null); setPage(1); }}
          >
            Tất cả
          </Button>
          {categories.map((cat) => (
            <Button
              key={cat.id}
              variant={selectedCategory === cat.id ? "default" : "outline"}
              size="sm"
              onClick={() => { setSelectedCategory(cat.id); setPage(1); }}
            >
              {cat.name}
            </Button>
          ))}
        </div>
      )}

      {/* Products grid */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : productsData?.items.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground">
          Chưa có sản phẩm nào
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {productsData?.items.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>

          {/* Pagination */}
          {productsData && productsData.pages > 1 && (
            <div className="flex justify-center gap-2">
              <Button variant="outline" disabled={page === 1} onClick={() => setPage(p => p - 1)}>
                Trước
              </Button>
              <span className="flex items-center px-4 text-sm text-muted-foreground">
                {page} / {productsData.pages}
              </span>
              <Button variant="outline" disabled={page >= productsData.pages} onClick={() => setPage(p => p + 1)}>
                Tiếp
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

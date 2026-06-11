// Auth
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  avatar_url?: string;
  role: "customer" | "admin";
  is_active: boolean;
  created_at: string;
}

// Category
export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image_url?: string;
  parent_id?: number;
  is_active: boolean;
  sort_order: number;
  children: Category[];
}

// Product
export interface ProductVariant {
  id: number;
  product_id: number;
  sku: string;
  name: string;
  price: number;
  compare_price?: number;
  stock: number;
  weight?: number;
  is_active: boolean;
}

export interface ProductImage {
  id: number;
  url: string;
  alt_text?: string;
  is_primary: boolean;
  sort_order: number;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description?: string;
  category_id?: number;
  category?: Category;
  is_active: boolean;
  is_featured: boolean;
  created_at: string;
  variants: ProductVariant[];
  images: ProductImage[];
  avg_rating?: number;
  review_count: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Cart
export interface CartItem {
  id: number;
  variant_id: number;
  quantity: number;
  variant: ProductVariant;
  created_at: string;
}

export interface CartResponse {
  items: CartItem[];
  total_items: number;
  subtotal: number;
}

// Order
export interface OrderItem {
  id: number;
  product_name: string;
  variant_name: string;
  sku: string;
  price: number;
  quantity: number;
  subtotal: number;
}

export interface Order {
  id: number;
  order_code: string;
  status: "pending" | "confirmed" | "shipping" | "delivered" | "cancelled" | "refunded";
  payment_method: string;
  payment_status: string;
  shipping_name: string;
  shipping_phone: string;
  shipping_address: string;
  subtotal: number;
  shipping_fee: number;
  discount_amount: number;
  total: number;
  note?: string;
  created_at: string;
  items: OrderItem[];
}

export interface Address {
  id: number;
  user_id: number;
  full_name: string;
  phone: string;
  province: string;
  district: string;
  ward: string;
  street: string;
  is_default: boolean;
}

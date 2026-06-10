from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ─── Common ───────────────────────────────────────────────
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int


# ─── Auth ─────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6, max_length=100)
    phone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r"^(0|\+84)[3-9]\d{8}$", v):
            raise ValueError("Số điện thoại không hợp lệ")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ─── User ─────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: str | None = None
    avatar_url: str | None = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = None
    avatar_url: str | None = None


# ─── Address ──────────────────────────────────────────────
class AddressCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str
    province: str
    district: str
    ward: str
    street: str
    is_default: bool = False


class AddressResponse(AddressCreate):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


# ─── Category ─────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    image_url: str | None = None
    parent_id: int | None = None
    is_active: bool = True
    sort_order: int = 0


class CategoryUpdate(CategoryCreate):
    name: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    parent_id: int | None
    is_active: bool
    sort_order: int
    children: list["CategoryResponse"] = []

    model_config = {"from_attributes": True}


# ─── Product ──────────────────────────────────────────────
class ProductVariantCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    compare_price: Decimal | None = None
    stock: int = Field(ge=0, default=0)
    weight: int | None = None
    is_active: bool = True


class ProductVariantResponse(ProductVariantCreate):
    id: int
    product_id: int

    model_config = {"from_attributes": True}


class ProductImageResponse(BaseModel):
    id: int
    url: str
    alt_text: str | None
    is_primary: bool
    sort_order: int

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    category_id: int | None = None
    is_active: bool = True
    is_featured: bool = False
    variants: list[ProductVariantCreate] = Field(min_length=1)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    category_id: int | None = None
    is_active: bool | None = None
    is_featured: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    category_id: int | None
    is_active: bool
    is_featured: bool
    created_at: datetime
    variants: list[ProductVariantResponse] = []
    images: list[ProductImageResponse] = []
    category: CategoryResponse | None = None
    avg_rating: float | None = None
    review_count: int = 0

    model_config = {"from_attributes": True}


# ─── Cart ─────────────────────────────────────────────────
class CartItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(ge=1, default=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    variant: ProductVariantResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_items: int
    subtotal: Decimal


# ─── Order ────────────────────────────────────────────────
class OrderCreate(BaseModel):
    address_id: int
    payment_method: str = "cod"
    note: str | None = None


class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    variant_name: str
    sku: str
    price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    order_code: str
    status: str
    payment_method: str
    payment_status: str
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total: Decimal
    note: str | None
    created_at: datetime
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str
    cancelled_reason: str | None = None


# ─── Review ───────────────────────────────────────────────
class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: str | None
    is_approved: bool
    created_at: datetime
    user: UserResponse | None = None

    model_config = {"from_attributes": True}


# ─── Upload ───────────────────────────────────────────────
class UploadResponse(BaseModel):
    url: str
    key: str

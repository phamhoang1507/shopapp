from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from slugify import slugify
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.models import Category, CartItem, ProductVariant, Order
from app.schemas.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse,
    OrderCreate, OrderResponse, OrderStatusUpdate, PaginatedResponse,
    UserResponse, UserUpdate,
)
from app.services.order_service import OrderService
from app.services.user_service import UserService
import math

# ─── Categories ───────────────────────────────────────────
categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@categories_router.get("", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.children))
        .where(Category.parent_id == None, Category.is_active == True)
        .order_by(Category.sort_order)
    )
    return result.scalars().all()


@categories_router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    slug = slugify(data.name, allow_unicode=True)
    existing = await db.scalar(select(Category).where(Category.slug == slug))
    if existing:
        slug = f"{slug}-{Category.id}"

    cat = Category(slug=slug, **data.model_dump())
    db.add(cat)
    await db.flush()
    return cat


@categories_router.put("/{cat_id}", response_model=CategoryResponse)
async def update_category(cat_id: int, data: CategoryUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    cat = await db.get(Category, cat_id)
    if not cat:
        raise HTTPException(404, "Không tìm thấy danh mục")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cat, k, v)
    await db.flush()
    return cat


@categories_router.delete("/{cat_id}", status_code=204)
async def delete_category(cat_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    cat = await db.get(Category, cat_id)
    if not cat:
        raise HTTPException(404, "Không tìm thấy danh mục")
    await db.delete(cat)


# ─── Cart ─────────────────────────────────────────────────
cart_router = APIRouter(prefix="/cart", tags=["Cart"])


@cart_router.get("", response_model=CartResponse)
async def get_cart(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from decimal import Decimal
    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.variant))
        .where(CartItem.user_id == current_user.id)
    )
    items = result.scalars().all()
    subtotal = sum(i.variant.price * i.quantity for i in items)
    return CartResponse(
        items=items,
        total_items=len(items),
        subtotal=subtotal,
    )


@cart_router.post("", response_model=CartItemResponse, status_code=201)
async def add_to_cart(data: CartItemCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    variant = await db.get(ProductVariant, data.variant_id)
    if not variant or not variant.is_active:
        raise HTTPException(404, "Sản phẩm không tồn tại")
    if variant.stock < data.quantity:
        raise HTTPException(400, f"Chỉ còn {variant.stock} sản phẩm")

    existing = await db.scalar(
        select(CartItem).where(CartItem.user_id == current_user.id, CartItem.variant_id == data.variant_id)
    )
    if existing:
        existing.quantity += data.quantity
        await db.flush()
        return existing

    item = CartItem(user_id=current_user.id, variant_id=data.variant_id, quantity=data.quantity)
    db.add(item)
    await db.flush()

    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.variant)).where(CartItem.id == item.id)
    )
    return result.scalar_one()


@cart_router.put("/{item_id}", response_model=CartItemResponse)
async def update_cart_item(item_id: int, data: CartItemUpdate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await db.get(CartItem, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(404, "Không tìm thấy")
    item.quantity = data.quantity
    await db.flush()
    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.variant)).where(CartItem.id == item_id)
    )
    return result.scalar_one()


@cart_router.delete("/{item_id}", status_code=204)
async def remove_from_cart(item_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await db.get(CartItem, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(404, "Không tìm thấy")
    await db.delete(item)


@cart_router.delete("", status_code=204)
async def clear_cart(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).where(CartItem.user_id == current_user.id))
    for item in result.scalars().all():
        await db.delete(item)


# ─── Orders ───────────────────────────────────────────────
orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.post("", response_model=OrderResponse, status_code=201)
async def create_order(data: OrderCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await OrderService.create_from_cart(db, current_user.id, data)


@orders_router.get("/my", response_model=PaginatedResponse)
async def my_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * size
    items, total = await OrderService.list_by_user(db, current_user.id, skip, size)
    return PaginatedResponse(
        items=[OrderResponse.model_validate(o) for o in items],
        total=total, page=page, size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@orders_router.get("/my/{order_id}", response_model=OrderResponse)
async def get_my_order(order_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = await OrderService.get_by_id(db, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(404, "Không tìm thấy đơn hàng")
    return order


@orders_router.post("/my/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = await OrderService.get_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Không tìm thấy đơn hàng")
    return await OrderService.cancel_by_user(db, order, current_user.id)


# Admin order endpoints
@orders_router.get("", response_model=PaginatedResponse)
async def list_all_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    _=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * size
    items, total = await OrderService.list_all(db, skip, size, status)
    return PaginatedResponse(
        items=[OrderResponse.model_validate(o) for o in items],
        total=total, page=page, size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@orders_router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: int, data: OrderStatusUpdate, _=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    order = await OrderService.get_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Không tìm thấy đơn hàng")
    return await OrderService.update_status(db, order, data)


# ─── Users (admin) ────────────────────────────────────────
users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me/addresses")
async def get_addresses(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from app.models.models import Address
    result = await db.execute(select(Address).where(Address.user_id == current_user.id))
    return result.scalars().all()


@users_router.post("/me/addresses", status_code=201)
async def add_address(data, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from app.models.models import Address
    from app.schemas.schemas import AddressCreate, AddressResponse
    address = Address(user_id=current_user.id, **data.model_dump())
    if data.is_default:
        existing = await db.execute(select(Address).where(Address.user_id == current_user.id, Address.is_default == True))
        for a in existing.scalars().all():
            a.is_default = False
    db.add(address)
    await db.flush()
    return address


@users_router.put("/me", response_model=UserResponse)
async def update_profile(data: UserUpdate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await UserService.update(db, current_user, data)


@users_router.get("", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * size
    items, total = await UserService.list_all(db, skip, size)
    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in items],
        total=total, page=page, size=size,
        pages=math.ceil(total / size) if total else 0,
    )

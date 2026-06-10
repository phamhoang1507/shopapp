import random
import string
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.models import Order, OrderItem, CartItem, Address, ProductVariant
from app.schemas.schemas import OrderCreate, OrderStatusUpdate


def generate_order_code() -> str:
    """SP240615XXXX"""
    date = datetime.now(timezone.utc).strftime("%y%m%d")
    suffix = "".join(random.choices(string.digits, k=4))
    return f"SP{date}{suffix}"


class OrderService:
    @staticmethod
    async def create_from_cart(db: AsyncSession, user_id: int, data: OrderCreate) -> Order:
        # Lấy cart items
        result = await db.execute(
            select(CartItem)
            .options(selectinload(CartItem.variant))
            .where(CartItem.user_id == user_id)
        )
        cart_items = result.scalars().all()
        if not cart_items:
            raise HTTPException(400, "Giỏ hàng trống")

        # Lấy địa chỉ
        address = await db.get(Address, data.address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(400, "Địa chỉ không hợp lệ")

        # Kiểm tra stock và tính tiền
        order_items_data = []
        subtotal = Decimal("0")

        for item in cart_items:
            variant = item.variant
            if not variant.is_active:
                raise HTTPException(400, f"Sản phẩm '{variant.name}' không còn bán")
            if variant.stock < item.quantity:
                raise HTTPException(400, f"'{variant.name}' chỉ còn {variant.stock} sản phẩm")

            item_subtotal = variant.price * item.quantity
            subtotal += item_subtotal
            order_items_data.append({
                "variant": variant,
                "quantity": item.quantity,
                "subtotal": item_subtotal,
            })

        shipping_fee = Decimal("30000") if subtotal < 500000 else Decimal("0")
        total = subtotal + shipping_fee

        # Tạo order
        order = Order(
            order_code=generate_order_code(),
            user_id=user_id,
            shipping_name=address.full_name,
            shipping_phone=address.phone,
            shipping_address=f"{address.street}, {address.ward}, {address.district}, {address.province}",
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            discount_amount=Decimal("0"),
            total=total,
            payment_method=data.payment_method,
            note=data.note,
        )
        db.add(order)
        await db.flush()

        # Tạo order items + trừ stock
        for item_data in order_items_data:
            variant = item_data["variant"]
            order_item = OrderItem(
                order_id=order.id,
                variant_id=variant.id,
                product_name=variant.product.name if hasattr(variant, 'product') else "N/A",
                variant_name=variant.name,
                sku=variant.sku,
                price=variant.price,
                quantity=item_data["quantity"],
                subtotal=item_data["subtotal"],
            )
            db.add(order_item)
            variant.stock -= item_data["quantity"]

        # Xóa cart
        for item in cart_items:
            await db.delete(item)

        await db.flush()
        return await OrderService.get_by_id(db, order.id)

    @staticmethod
    async def get_by_id(db: AsyncSession, order_id: int) -> Order | None:
        result = await db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20):
        from sqlalchemy import func
        total = await db.scalar(
            select(func.count()).where(Order.user_id == user_id)
        )
        result = await db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    @staticmethod
    async def list_all(db: AsyncSession, skip: int = 0, limit: int = 20, status: str | None = None):
        from sqlalchemy import func
        q = select(Order).options(selectinload(Order.items))
        if status:
            q = q.where(Order.status == status)
        total = await db.scalar(select(func.count()).select_from(q.subquery()))
        result = await db.execute(q.order_by(Order.created_at.desc()).offset(skip).limit(limit))
        return result.scalars().all(), total

    @staticmethod
    async def update_status(db: AsyncSession, order: Order, data: OrderStatusUpdate) -> Order:
        allowed = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["shipping", "cancelled"],
            "shipping": ["delivered"],
            "delivered": ["refunded"],
        }
        if data.status not in allowed.get(order.status, []):
            raise HTTPException(400, f"Không thể chuyển từ '{order.status}' sang '{data.status}'")

        order.status = data.status
        if data.cancelled_reason:
            order.cancelled_reason = data.cancelled_reason
        await db.flush()
        return order

    @staticmethod
    async def cancel_by_user(db: AsyncSession, order: Order, user_id: int) -> Order:
        if order.user_id != user_id:
            raise HTTPException(403, "Không có quyền")
        if order.status != "pending":
            raise HTTPException(400, "Chỉ hủy được đơn đang chờ xác nhận")

        # Hoàn stock
        result = await db.execute(
            select(OrderItem).options(selectinload(OrderItem.variant)).where(OrderItem.order_id == order.id)
        )
        for item in result.scalars().all():
            item.variant.stock += item.quantity

        order.status = "cancelled"
        await db.flush()
        return order

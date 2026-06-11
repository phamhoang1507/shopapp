"""
Chạy: python seed.py
Tạo: 1 admin, 1 customer, 3 categories, 6 sản phẩm mẫu
"""
import asyncio
import sys
sys.path.insert(0, ".")

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.models import User, Category, Product, ProductVariant
from slugify import slugify


async def seed():
    async with AsyncSessionLocal() as db:
        # ── Users ──────────────────────────────────────
        admin = User(
            email="admin@shopapp.com",
            full_name="Admin ShopApp",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
        )
        customer = User(
            email="user@shopapp.com",
            full_name="Nguyễn Văn A",
            hashed_password=hash_password("user123"),
            role="customer",
            is_active=True,
        )
        db.add(admin)
        db.add(customer)
        await db.flush()
        print(f"✅ Users: admin@shopapp.com / admin123  |  user@shopapp.com / user123")

        # ── Categories ─────────────────────────────────
        cats = [
            Category(name="Áo", slug="ao", is_active=True, sort_order=1),
            Category(name="Quần", slug="quan", is_active=True, sort_order=2),
            Category(name="Phụ kiện", slug="phu-kien", is_active=True, sort_order=3),
        ]
        for c in cats:
            db.add(c)
        await db.flush()
        print(f"✅ Categories: {[c.name for c in cats]}")

        # ── Products ───────────────────────────────────
        products_data = [
            {
                "name": "Áo Thun Basic Trắng",
                "category": cats[0],
                "description": "Áo thun cotton 100%, form regular fit, phù hợp mọi dịp.",
                "variants": [
                    {"sku": "AT-WHITE-S", "name": "S", "price": 199000, "compare_price": 250000, "stock": 50},
                    {"sku": "AT-WHITE-M", "name": "M", "price": 199000, "compare_price": 250000, "stock": 80},
                    {"sku": "AT-WHITE-L", "name": "L", "price": 199000, "compare_price": 250000, "stock": 60},
                    {"sku": "AT-WHITE-XL", "name": "XL", "price": 219000, "compare_price": 270000, "stock": 30},
                ],
            },
            {
                "name": "Áo Polo Nam Classic",
                "category": cats[0],
                "description": "Áo polo chất liệu pique cotton, cổ bẻ thanh lịch.",
                "variants": [
                    {"sku": "POLO-NAVY-M", "name": "M / Navy", "price": 350000, "compare_price": 450000, "stock": 40},
                    {"sku": "POLO-NAVY-L", "name": "L / Navy", "price": 350000, "compare_price": 450000, "stock": 35},
                    {"sku": "POLO-WHITE-M", "name": "M / Trắng", "price": 350000, "compare_price": 450000, "stock": 25},
                ],
            },
            {
                "name": "Áo Khoác Denim",
                "category": cats[0],
                "description": "Áo khoác jeans denim dày dặn, phong cách Streetwear.",
                "variants": [
                    {"sku": "DENIM-S", "name": "S", "price": 650000, "compare_price": 850000, "stock": 20},
                    {"sku": "DENIM-M", "name": "M", "price": 650000, "compare_price": 850000, "stock": 30},
                    {"sku": "DENIM-L", "name": "L", "price": 680000, "compare_price": 880000, "stock": 15},
                ],
            },
            {
                "name": "Quần Jean Slim Fit",
                "category": cats[1],
                "description": "Quần jean denim co giãn nhẹ, form slim fit hiện đại.",
                "variants": [
                    {"sku": "JEAN-28", "name": "28", "price": 450000, "compare_price": 580000, "stock": 25},
                    {"sku": "JEAN-29", "name": "29", "price": 450000, "compare_price": 580000, "stock": 30},
                    {"sku": "JEAN-30", "name": "30", "price": 450000, "compare_price": 580000, "stock": 40},
                    {"sku": "JEAN-31", "name": "31", "price": 450000, "compare_price": 580000, "stock": 20},
                    {"sku": "JEAN-32", "name": "32", "price": 450000, "compare_price": 580000, "stock": 15},
                ],
            },
            {
                "name": "Quần Shorts Kaki",
                "category": cats[1],
                "description": "Quần short kaki lịch sự, phù hợp đi chơi và đi làm.",
                "variants": [
                    {"sku": "SHORTS-KAKI-S", "name": "S / Be", "price": 280000, "stock": 35},
                    {"sku": "SHORTS-KAKI-M", "name": "M / Be", "price": 280000, "stock": 45},
                    {"sku": "SHORTS-KAKI-L", "name": "L / Xanh", "price": 280000, "stock": 30},
                ],
            },
            {
                "name": "Mũ Bucket Hat",
                "category": cats[2],
                "description": "Mũ bucket vải canvas, chống nắng tốt, nhiều màu sắc.",
                "is_featured": True,
                "variants": [
                    {"sku": "HAT-BLACK", "name": "Đen", "price": 150000, "compare_price": 200000, "stock": 60},
                    {"sku": "HAT-WHITE", "name": "Trắng", "price": 150000, "compare_price": 200000, "stock": 55},
                    {"sku": "HAT-BEIGE", "name": "Be", "price": 150000, "compare_price": 200000, "stock": 40},
                ],
            },
        ]

        for pd in products_data:
            slug = slugify(pd["name"], allow_unicode=True)
            product = Product(
                name=pd["name"],
                slug=slug,
                description=pd["description"],
                category_id=pd["category"].id,
                is_active=True,
                is_featured=pd.get("is_featured", False),
            )
            db.add(product)
            await db.flush()

            for vd in pd["variants"]:
                variant = ProductVariant(
                    product_id=product.id,
                    sku=vd["sku"],
                    name=vd["name"],
                    price=vd["price"],
                    compare_price=vd.get("compare_price"),
                    stock=vd["stock"],
                    is_active=True,
                )
                db.add(variant)

            print(f"  ✅ Product: {pd['name']} ({len(pd['variants'])} variants)")

        await db.commit()
        print("\n🎉 Seed hoàn thành!")
        print("   Admin:    admin@shopapp.com / admin123")
        print("   Customer: user@shopapp.com  / user123")


if __name__ == "__main__":
    asyncio.run(seed())
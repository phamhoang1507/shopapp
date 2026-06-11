from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.api.v1.router import api_router


async def run_seed():
    """Chạy seed lần đầu nếu chưa có admin"""
    from sqlalchemy import select
    from app.models.models import User, Category, Product, ProductVariant
    from app.core.security import hash_password
    from slugify import slugify

    async with AsyncSessionLocal() as db:
        # Kiểm tra đã seed chưa
        existing = await db.scalar(select(User).where(User.email == "admin@shopapp.com"))
        if existing:
            return  # Đã seed rồi, bỏ qua

        print("🌱 Chạy seed data lần đầu...")

        # Users
        admin = User(email="admin@shopapp.com", full_name="Admin ShopApp",
                     hashed_password=hash_password("admin123"), role="admin", is_active=True)
        customer = User(email="user@shopapp.com", full_name="Nguyễn Văn A",
                        hashed_password=hash_password("user123"), role="customer", is_active=True)
        db.add(admin)
        db.add(customer)
        await db.flush()

        # Categories
        cats = [
            Category(name="Áo", slug="ao", is_active=True, sort_order=1),
            Category(name="Quần", slug="quan", is_active=True, sort_order=2),
            Category(name="Phụ kiện", slug="phu-kien", is_active=True, sort_order=3),
        ]
        for c in cats:
            db.add(c)
        await db.flush()

        # Products
        products_data = [
            {
                "name": "Áo Thun Basic Trắng", "category": cats[0],
                "description": "Áo thun cotton 100%, form regular fit.",
                "variants": [
                    {"sku": "AT-WHITE-S", "name": "S", "price": 199000, "compare_price": 250000, "stock": 50},
                    {"sku": "AT-WHITE-M", "name": "M", "price": 199000, "compare_price": 250000, "stock": 80},
                    {"sku": "AT-WHITE-L", "name": "L", "price": 199000, "compare_price": 250000, "stock": 60},
                ],
            },
            {
                "name": "Áo Polo Nam Classic", "category": cats[0],
                "description": "Áo polo chất liệu pique cotton, cổ bẻ thanh lịch.",
                "variants": [
                    {"sku": "POLO-NAVY-M", "name": "M / Navy", "price": 350000, "compare_price": 450000, "stock": 40},
                    {"sku": "POLO-WHITE-M", "name": "M / Trắng", "price": 350000, "compare_price": 450000, "stock": 25},
                ],
            },
            {
                "name": "Quần Jean Slim Fit", "category": cats[1],
                "description": "Quần jean denim co giãn nhẹ, form slim fit.",
                "variants": [
                    {"sku": "JEAN-29", "name": "29", "price": 450000, "compare_price": 580000, "stock": 30},
                    {"sku": "JEAN-30", "name": "30", "price": 450000, "compare_price": 580000, "stock": 40},
                    {"sku": "JEAN-31", "name": "31", "price": 450000, "compare_price": 580000, "stock": 20},
                ],
            },
            {
                "name": "Mũ Bucket Hat", "category": cats[2],
                "description": "Mũ bucket vải canvas, chống nắng tốt.",
                "is_featured": True,
                "variants": [
                    {"sku": "HAT-BLACK", "name": "Đen", "price": 150000, "compare_price": 200000, "stock": 60},
                    {"sku": "HAT-WHITE", "name": "Trắng", "price": 150000, "compare_price": 200000, "stock": 55},
                ],
            },
        ]

        for pd in products_data:
            product = Product(
                name=pd["name"],
                slug=slugify(pd["name"], allow_unicode=True),
                description=pd["description"],
                category_id=pd["category"].id,
                is_active=True,
                is_featured=pd.get("is_featured", False),
            )
            db.add(product)
            await db.flush()
            for vd in pd["variants"]:
                db.add(ProductVariant(
                    product_id=product.id,
                    sku=vd["sku"], name=vd["name"],
                    price=vd["price"],
                    compare_price=vd.get("compare_price"),
                    stock=vd["stock"],
                    is_active=True,
                ))

        await db.commit()
        print("✅ Seed xong! admin@shopapp.com / admin123")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tạo tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed data lần đầu
    await run_seed()
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="ShopApp API - Hệ thống bán hàng",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
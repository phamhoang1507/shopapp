from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from slugify import slugify
from app.models.models import Product, ProductVariant, ProductImage, Category
from app.schemas.schemas import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    async def _unique_slug(db: AsyncSession, name: str, exclude_id: int | None = None) -> str:
        base = slugify(name, allow_unicode=True)
        slug = base
        i = 1
        while True:
            q = select(Product).where(Product.slug == slug)
            if exclude_id:
                q = q.where(Product.id != exclude_id)
            existing = await db.scalar(q)
            if not existing:
                return slug
            slug = f"{base}-{i}"
            i += 1

    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: int) -> Product | None:
        result = await db.execute(
            select(Product)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
                selectinload(Product.category),
            )
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Product | None:
        result = await db.execute(
            select(Product)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
                selectinload(Product.category),
            )
            .where(Product.slug == slug, Product.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_products(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        search: str | None = None,
        is_featured: bool | None = None,
        is_active: bool = True,
    ) -> tuple[list[Product], int]:
        q = select(Product).options(
            selectinload(Product.variants),
            selectinload(Product.images),
            selectinload(Product.category),
        )

        if is_active is not None:
            q = q.where(Product.is_active == is_active)
        if category_id:
            q = q.where(Product.category_id == category_id)
        if is_featured is not None:
            q = q.where(Product.is_featured == is_featured)
        if search:
            q = q.where(Product.name.ilike(f"%{search}%"))

        total_q = select(func.count()).select_from(q.subquery())
        total = await db.scalar(total_q)

        result = await db.execute(
            q.order_by(Product.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    @staticmethod
    async def create(db: AsyncSession, data: ProductCreate) -> Product:
        slug = await ProductService._unique_slug(db, data.name)

        product = Product(
            name=data.name,
            slug=slug,
            description=data.description,
            category_id=data.category_id,
            is_active=data.is_active,
            is_featured=data.is_featured,
        )
        db.add(product)
        await db.flush()

        for v in data.variants:
            variant = ProductVariant(product_id=product.id, **v.model_dump())
            db.add(variant)

        await db.flush()
        return await ProductService.get_by_id(db, product.id)

    @staticmethod
    async def update(db: AsyncSession, product: Product, data: ProductUpdate) -> Product:
        update_data = data.model_dump(exclude_none=True)
        if "name" in update_data:
            update_data["slug"] = await ProductService._unique_slug(db, update_data["name"], product.id)
        for field, value in update_data.items():
            setattr(product, field, value)
        await db.flush()
        return await ProductService.get_by_id(db, product.id)

    @staticmethod
    async def add_image(db: AsyncSession, product_id: int, url: str, is_primary: bool = False) -> ProductImage:
        if is_primary:
            # Unset other primary images
            existing = await db.execute(
                select(ProductImage).where(ProductImage.product_id == product_id, ProductImage.is_primary == True)
            )
            for img in existing.scalars().all():
                img.is_primary = False

        image = ProductImage(product_id=product_id, url=url, is_primary=is_primary)
        db.add(image)
        await db.flush()
        return image

    @staticmethod
    async def delete(db: AsyncSession, product: Product):
        await db.delete(product)
        await db.flush()

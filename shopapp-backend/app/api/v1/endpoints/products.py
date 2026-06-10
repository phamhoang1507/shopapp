from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.schemas.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, UploadResponse, PaginatedResponse
)
from app.services.product_service import ProductService
from app.services.r2_service import r2_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=PaginatedResponse)
async def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    search: str | None = None,
    is_featured: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * size
    items, total = await ProductService.list_products(
        db, skip=skip, limit=size,
        category_id=category_id, search=search, is_featured=is_featured,
    )
    import math
    return PaginatedResponse(
        items=[ProductResponse.model_validate(p) for p in items],
        total=total, page=page, size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    return product


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    product = await ProductService.get_by_slug(db, slug)
    if not product:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    return product


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await ProductService.create(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    product = await ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    return await ProductService.update(db, product, data)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    product = await ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    await ProductService.delete(db, product)


@router.post("/{product_id}/images", response_model=UploadResponse)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    is_primary: bool = False,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    product = await ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Không tìm thấy sản phẩm")

    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Chỉ chấp nhận file ảnh")

    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, "Ảnh không được vượt quá 10MB")

    result = await r2_service.upload_image(data, folder="products", original_filename=file.filename)
    await ProductService.add_image(db, product_id, result["url"], is_primary)
    return UploadResponse(**result)

from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.other import (
    categories_router,
    cart_router,
    orders_router,
    users_router,
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(categories_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(users_router)

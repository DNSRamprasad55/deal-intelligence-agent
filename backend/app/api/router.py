from fastapi import APIRouter
from app.api.routes import health, auth, companies, deals, interactions, intelligence

api_router = APIRouter()

# Root health endpoint
api_router.include_router(health.router)

# Versioned API routes under /api
v1_router = APIRouter(prefix="/api")
v1_router.include_router(auth.router)
v1_router.include_router(companies.router)
v1_router.include_router(deals.router)
v1_router.include_router(interactions.router)
v1_router.include_router(intelligence.router)

api_router.include_router(v1_router)

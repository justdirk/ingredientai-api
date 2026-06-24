"""IngredientAI API — FastAPI entrypoint.

Phase 0 skeleton: health + router wiring. Pairing endpoints are stubbed and
become live in Phase 1 once the owned graph (FlavorDB2 + FlavorGraph + USDA) is
ingested into Supabase.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import settings
from routes import pairing

app = FastAPI(title="IngredientAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pairing.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment, "version": "0.1.0"}

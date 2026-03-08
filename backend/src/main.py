from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.router import router as auth_router
from .api.assets import router as assets_router
from .api.audit import router as audit_router
from .api.admin import router as admin_router

app = FastAPI(
    title="Argos Asset Management API",
    description="KT Argos - Company Asset Self-Survey and Admin Query System",
    version="1.0.0",
)

# CORS for frontend (Azure Static Web Apps + local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.azurestaticapps.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(assets_router, prefix="/assets", tags=["Assets"])
app.include_router(audit_router, prefix="/audit", tags=["Audit"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

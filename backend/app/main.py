"""
AI Review Verification System — Main FastAPI Application
Phase 2: Database, Vision Analysis, Real Order Verification

Powered by:
  • LangGraph — Multi-agent orchestration (7 nodes)
  • LangChain — Agent/tool abstractions
  • Groq — Llama 3.3 70B (text) + Llama 4 Scout (vision)
  • LangSmith — Tracing & observability
  • SQLite — Order/review database
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.review import router as review_router
from app.routes.tools import router as tools_router
from app.routes.orders import router as orders_router
from app.routes.reviews import router as reviews_router
from app.database.db import init_db
from app.database.seed import seed_database

# Initialize config (loads env vars, sets up LangSmith)
import app.core.config as config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup."""
    print("\n🚀 Starting AI Review Verification System v2.0...")
    init_db()
    seed_database()
    print("✅ System ready!\n")
    yield
    print("\n👋 Shutting down...")


app = FastAPI(
    title="AI Review Verification System",
    description="Multi-agent review trust verification with database, vision analysis, and real order verification",
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory=config.UPLOADS_DIR), name="uploads")

# API routes
app.include_router(review_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(tools_router, prefix="/tools")


@app.get("/")
def root():
    return {
        "status": "Backend running",
        "version": "2.0.0",
        "engine": "LangGraph + LangChain + Groq",
        "agents": 7,
        "custom_tools": 3,
        "tracing": "LangSmith",
        "database": "SQLite",
        "vision": "Llama 4 Scout (image analysis)",
        "endpoints": {
            "review_flow": "/api/review",
            "order_lookup": "/api/orders/lookup?order_id=...",
            "businesses": "/api/businesses",
            "review_history": "/api/reviews",
            "tools": "/tools",
            "docs": "/docs",
        },
    }

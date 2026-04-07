from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import quran

settings = get_settings()

app = FastAPI(
    title="Quran Mobile API",
    description="Backend API pour l'application Quran Mobile",
    version="1.0.0",
)

# CORS - Important pour Flutter
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(quran.router)


@app.get("/")
async def root():
    return {
        "message": "Quran Mobile API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "chapters": "/api/quran/chapters",
            "verses": "/api/quran/chapters/{id}/verses",
            "translations": "/api/quran/translations",
            "recitations": "/api/quran/recitations",
            "search": "/api/quran/search",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

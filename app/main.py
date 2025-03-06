from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.api.endpoints import router as api_router

# Create FastAPI app
app = FastAPI(
    title="Smart Packaging Recommender",
    description="AI-powered packaging material recommendations",
    version="1.0.0"
)

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the main UI page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# Add error handlers
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_message": str(exc)
        },
        status_code=500
    )
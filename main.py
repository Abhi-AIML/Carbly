import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import chat, carbon

import time
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("carbly")

# Simple in-memory rate limiter
RATE_LIMIT = 30  # requests
RATE_LIMIT_WINDOW = 60  # seconds
ip_request_times: dict[str, list[float]] = defaultdict(list)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Carbly",
    description="Carbon Footprint Awareness Platform",
    version="1.0.0",
    docs_url=None,    # Disable Swagger in production
    redoc_url=None,   # Disable ReDoc in production
)

@app.middleware("http")
async def rate_limit_and_security_middleware(request: Request, call_next):
    """Rate limiting and security headers middleware."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Clean up old requests outside the rate limit window
    ip_request_times[client_ip] = [
        t for t in ip_request_times[client_ip]
        if now - t < RATE_LIMIT_WINDOW
    ]
    
    if len(ip_request_times[client_ip]) >= RATE_LIMIT:
        logger.warning("Rate limit exceeded for IP: %s", client_ip)
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    ip_request_times[client_ip].append(now)
    
    # Process request
    response = await call_next(request)
    
    # Set Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    return response

# CORS middleware configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Include routers
app.include_router(chat.router, prefix="/api")
app.include_router(carbon.router, prefix="/api")

# Mount static files folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main SPA index page."""
    return FileResponse("static/index.html")

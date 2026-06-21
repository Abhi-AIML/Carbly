import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import chat, carbon

import time
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException

# Simple in-memory rate limiter
RATE_LIMIT = 30 # requests
RATE_LIMIT_WINDOW = 60 # seconds
ip_request_times = defaultdict(list)

# Load environment variables
load_dotenv()

app = FastAPI(title="Carbly", description="Carbon Footprint Awareness Platform")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    # Clean up old requests
    ip_request_times[client_ip] = [t for t in ip_request_times[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(ip_request_times[client_ip]) >= RATE_LIMIT:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})
    
    ip_request_times[client_ip].append(now)
    
    # Set Security Headers
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'"
    return response

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api")
app.include_router(carbon.router, prefix="/api")

# Mount static files folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

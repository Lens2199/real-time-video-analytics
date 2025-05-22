from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GitHub Pages URL for your repository
GITHUB_PAGES_URL = "https://lens2199.github.io"

# Create Socket.IO server with explicit CORS configuration
sio = socketio.AsyncServer(
    async_mode='asgi', 
    cors_allowed_origins=[
        'http://localhost:5173', 
        'http://127.0.0.1:5173', 
        GITHUB_PAGES_URL,
        'https://lens2199.github.io/real-time-video-analytics',
        '*'
    ],
    logger=False,  # Disable socket.io logging to reduce noise
    engineio_logger=False
)

# Create FastAPI app
app = FastAPI(title="AI Video Analysis System")

# Add CORS middleware with explicit allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        GITHUB_PAGES_URL,
        "https://lens2199.github.io/real-time-video-analytics",
        "*"
    ],
    allow_credentials=False,  # Set to False for cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO events
@sio.event
async def connect(sid, environ, auth):
    logger.info(f"Client connected: {sid}")
    await sio.emit('connection_status', {'status': 'connected'}, room=sid)

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def ping(sid, data):
    await sio.emit('pong', {'message': 'Server is alive'}, room=sid)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to AI Video Analysis API", "status": "running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Import and include API routes
from app.api.routes import router as api_router
app.include_router(api_router, prefix="/api")

# Create the combined ASGI app
socket_app = socketio.ASGIApp(sio, app)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the server...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the server...")

# Export the socket_app as the main application
application = socket_app
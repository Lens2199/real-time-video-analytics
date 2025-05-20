from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=['*'])
socket_app = socketio.ASGIApp(sio)

# Create FastAPI app
app = FastAPI(title="AI Video Analysis System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
app.mount('/socket.io', socket_app)

# Socket.IO events
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to AI Video Analysis API"}

# Import and include API routes
from app.api.routes import router as api_router
app.include_router(api_router, prefix="/api")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the server...")
    # You can add initialization code here (like loading AI models)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the server...")
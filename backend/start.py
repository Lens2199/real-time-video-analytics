import uvicorn
import os

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on host 0.0.0.0 and port {port}")
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",  # Must bind to 0.0.0.0 for Render
        port=port,       # Use Render's PORT environment variable
        reload=False,    # Disable reload in production
        workers=1,       # Single worker for free tier
        log_level="info"
    )
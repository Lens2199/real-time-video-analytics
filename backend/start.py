import uvicorn
import os

# Set environment variables for PyTorch compatibility
os.environ['TORCH_SERIALIZATION_SAFE_GLOBALS'] = '1'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on host 0.0.0.0 and port {port}")
    
    uvicorn.run(
        "app.main:application",  # Changed to use the combined ASGI app
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        log_level="info"
    )
import os

# Set environment variables BEFORE importing anything else
os.environ['TORCH_SERIALIZATION_SAFE_GLOBALS'] = '1'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['TORCH_HOME'] = '/tmp/torch'
os.environ['ULTRALYTICS_CONFIG_DIR'] = '/tmp/ultralytics'

# Disable PyTorch warnings
import warnings
warnings.filterwarnings("ignore")

import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on host 0.0.0.0 and port {port}")
    print(f"PyTorch environment variables set for production compatibility")
    
    uvicorn.run(
        "app.main:app",  # This should now work correctly
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        log_level="info"
    )
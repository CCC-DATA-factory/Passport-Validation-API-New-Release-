# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from turbojpeg import TurboJPEG
from core.logging import setup_logger
from app.api.v4.endpoints import passport
from prometheus_fastapi_instrumentator import Instrumentator

# ------------------------------------------------
# 1️⃣ Load environment variables early
# ------------------------------------------------
load_dotenv(".env")

jpeg_dll = os.getenv("TURBOJPEG_DLL_PATH")
if not jpeg_dll:
    raise RuntimeError("TURBOJPEG_DLL_PATH must be set in .env")

# Add DLL directory to PATH (Windows-safe)
dll_dir = os.path.dirname(jpeg_dll)
try:
    os.add_dll_directory(dll_dir)
except Exception:
    os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")

# ------------------------------------------------
# 2️⃣ Initialize logging
# ------------------------------------------------
logger = setup_logger()
logger.info("Logger initialized successfully")

# ------------------------------------------------
# 3️⃣ Initialize TurboJPEG
# ------------------------------------------------
try:
    jpeg = TurboJPEG(lib_path=jpeg_dll)
    logger.info(f"TurboJPEG loaded from: {jpeg_dll}")
except Exception as e:
    logger.error(f"Failed to initialize TurboJPEG: {e}")
    raise RuntimeError(f"TurboJPEG initialization failed: {e}")

# ------------------------------------------------
# 4️⃣ Create FastAPI app
# ------------------------------------------------
app = FastAPI(
    title=os.getenv("APP_NAME", "Passport MRZ API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="API to extract and validate MRZ data from passport images"
)
Instrumentator().instrument(app).expose(app)
# ------------------------------------------------
# 5️⃣ Configure CORS (adjust for production)
# ------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------
# 6️⃣ Include routers
# ------------------------------------------------
app.include_router(passport.router)

# ------------------------------------------------
# 7️⃣ Startup & Shutdown Events
# ------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("Passport MRZ API is starting...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Passport MRZ API is shutting down...")

# ------------------------------------------------
# 8️⃣ Entry point for uvicorn
# ------------------------------------------------
# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    logger.info("Running API in standalone mode")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

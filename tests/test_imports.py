# test_imports.py
import os
from dotenv import load_dotenv
load_dotenv(".env")

dll = os.getenv("TURBOJPEG_DLL_PATH")
if not dll:
    raise SystemExit("TURBOJPEG_DLL_PATH not set")

dirp = os.path.dirname(dll)
print("Adding dll dir:", dirp)
try:
    os.add_dll_directory(dirp)
except Exception:
    os.environ["PATH"] = dirp + os.pathsep + os.environ.get("PATH", "")

print("Trying to import turbojpeg...")
from turbojpeg import TurboJPEG
print("TurboJPEG imported OK")
jpeg = TurboJPEG(lib_path=dll)
print("TurboJPEG instance OK")

print("Trying to import mrzscanner...")
import mrzscanner
print("mrzscanner imported OK")

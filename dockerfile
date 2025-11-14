# ============================
# 📦 Stage 1: Base Image
# ============================
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# ============================
# 🔧 System Dependencies
# ============================
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libjpeg-turbo-progs \
    libjpeg62-turbo-dev \
    libturbojpeg0-dev \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    pkg-config \
    && ln -s /usr/lib/x86_64-linux-gnu/libturbojpeg.so.0 /usr/lib/x86_64-linux-gnu/libturbojpeg.so || true \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 📂 Working Directory
# ============================
WORKDIR /app

# ============================
# 🧾 Copy Files & Install Python Deps
# ============================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ============================
# ⚙️ Environment Variables
# ============================
ENV LOG_LEVEL=INFO
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV TURBOJPEG_DLL_PATH=/usr/lib/x86_64-linux-gnu/libturbojpeg.so

# ============================
# 🚀 Start FastAPI
# ============================
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

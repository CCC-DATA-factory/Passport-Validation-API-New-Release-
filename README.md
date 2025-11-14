# Passport Validation API (passport-validation-v4)

> FastAPI service that extracts, parses and validates passport MRZ (Machine Readable Zone) from images.
> Uses MRZScanner (detection + recognition) + PassportEye (parsing) + ICAO checksum validation.

---

## Features
- MRZ detection using `mrzscanner`
- MRZ parsing using `passporteye`
- Normalization & ICAO checksums
- Date normalization to `YYYY-MM-DD`
- File upload or `source` (local path / URL / base64)
- Prometheus metrics endpoint (`/metrics`) and Grafana-ready
- Dockerized, ready for CI/CD

---

## Table of Contents
- [Quick Start](#quick-start)
- [Endpoints](#endpoints)
- [Environment (.env)](#environment-env)
- [Examples (curl)](#examples-curl)
- [Docker & Docker Compose](#docker--docker-compose)
- [Prometheus & Grafana](#prometheus--grafana)
- [Common Errors & Troubleshooting](#common-errors--troubleshooting)
- [Branching & Git workflow (push to `passport-validation-v4`)](#branching--git-workflow-push-to-passport-validation-v4)
- [Contributing / Contact](#contributing--contact)

---

## Quick Start

### 1. Clone repo
```bash
git clone https://github.com/CCC-DATA-factory/Passport-Validation-API-New-Release-.git
cd Passport-Validation-API
---

## Overview & Architecture
This project:
- Detects MRZ lines in passport images using `mrzscanner`.
- Parses MRZ data using `passporteye`.
- Normalizes fields (strings, dates) and validates them using ICAO MRZ checksums.
- Provides a single endpoint `/v4/passport` that accepts either an uploaded file or a `source` (local path / URL / base64).
- Exposes Prometheus metrics for monitoring (optional).
- Designed to run locally, inside Docker, or in Kubernetes.

---

## Project structure

passport_api/
├─ app/
│ └─ api/
│ └─ v4/
│ ├─ deps.py
│ └─ endpoints/
│ └─ passport.py
├─ core/
│ └─ logging.py
├─ domain/
│ ├─ logic/
│ │ ├─ mrz_adapter.py # MRZ detector adapter (mrzscanner)
│ │ ├─ parser_adapter.py # parser adapter (passporteye)
│ │ └─ passport_service.py # orchestrates detection + parsing + validation
│ └─ models/
│ └─ mrz_data.py # Pydantic model for MRZ & normalized fields
├─ schemas/
│ ├─ request.py
│ └─ response.py
├─ services/
│ └─ persistence.py # optional
├─ utils/
│ ├─ image.py # image loader
│ └─ validators.py # MRZ checksum helpers & converters
├─ .env
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ main.py


---

## Requirements & install (local)

1. Create & activate venv:
```bash
python -m venv .venv
# linux/mac
source .venv/bin/activate
# windows
.venv\Scripts\activate

2. Install dependencies:
pip install -r requirements.txt

To build the container ,
1.  docker-compose build
2.  docker-compose up -d 

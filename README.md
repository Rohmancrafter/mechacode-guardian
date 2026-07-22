# MechaCode Guardian

**AI-powered maintenance co-worker for mechatronics technicians.**

> Competition submission for the AI Builders Challenge with IBM Bob — July 2026 Wildcard Challenge
> Theme: *Intelligent Systems for the Future of Work*

---

## Problem Statement

Mechatronics technicians in Indonesian manufacturing spend disproportionate time searching fragmented technical manuals, relying on colleague memory, and making trial-and-error repairs. Incorrect fault diagnosis on CNC machines, PLCs, or industrial robots can cause equipment damage or personal injury.

MechaCode Guardian addresses this by acting as an AI-powered maintenance co-worker: it grounds every answer in ingested technical documentation, shows explicit citations, flags hazardous scenarios for human escalation, and generates auditable diagnosis reports.

---

## AI Approach

| Role | Technology |
|---|---|
| AI development partner | IBM Bob (primary — all coding, architecture, documentation) |
| Primary LLM (diagnosis generation) | Gemini via the `google-genai` SDK |
| Optional future LLM | IBM Granite via watsonx.ai when credentials are available |
| Embeddings | `gemini-embedding-001` (3072-dim, bilingual) |
| Vector store | DataStax Astra DB — collection `mechacode_guardian_kb` |
| Document parsing | IBM Docling |

The system uses a **Retrieval-Augmented Generation (RAG)** pipeline: every diagnosis is grounded in retrieved chunks from synthetic technical documentation, with a deterministic safety gate that detects hazardous keywords before any LLM call.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full architecture.

---

## Architecture

```
Browser (React + Vite)
    │  REST: POST /api/v1/diagnose
    ▼
FastAPI Backend (Python)
    ├── Retrieval Module  →  Astra DB (ANN cosine, gemini-embedding-001)
    ├── Safety Gate       →  Deterministic keyword check (safety_triggers.json)
    ├── Generation Module →  ProviderRouter → IBM Granite (primary) / Gemini (fallback)
    └── Reporting Module  →  Markdown report assembly
```

Full diagram: [`docs/ARCHITECTURE.md §2`](docs/ARCHITECTURE.md#2-architecture-diagram)

---

## Selected Theme

**Intelligent Systems for the Future of Work** — MechaCode Guardian directly replaces fragmented, error-prone manual maintenance workflows with an AI co-worker for front-line industrial technicians.

---

## IBM Bob Usage

IBM Bob was the primary AI development partner for this project, used across architecture, coding, testing, documentation, and security review. Full auditable log: [`docs/IBM_BOB_USAGE.md`](docs/IBM_BOB_USAGE.md)

---

## Local Development

### Prerequisites

- Python 3.12
- Node.js 24 LTS + npm 11
- Active API credentials for Google AI and Astra DB
- Optional watsonx.ai credentials for future IBM Granite integration

### 1. Clone and configure environment

```powershell
# Copy the env template — fill in real values
Copy-Item .env.example .env
# Edit .env with your credentials (never commit .env)
```

### 2. Backend setup

```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Start the API server (http://localhost:8000)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation available at `http://localhost:8000/docs`

### 3. Frontend setup

```powershell
cd frontend

# Install dependencies
npm install

# Start Vite dev server (http://localhost:5173)
npm run dev
```

The frontend dev server proxies `/api/*` and `/health` to the backend automatically.

### 4. Dry-run the ingestion pipeline (no database or embedding calls)

```powershell
# Single document — validate, chunk, and summarise (dry-run only)
py -3.12 scripts/ingest.py --file knowledge/synthetic/MGC-MOTOR-001.md --dry-run

# All documents declared in the manifest
py -3.12 scripts/ingest.py --all --dry-run

# With verbose per-chunk preview
py -3.12 scripts/ingest.py --all --dry-run --verbose
```

Dry-run confirms: zero Astra DB writes, zero Gemini embedding calls, zero network requests.

### 5. Run backend tests

```powershell
# From project root (with .venv active)
py -3.12 -m pytest tests/unit -v
```

### 6. Validate frontend types

```powershell
cd frontend
npm run type-check
```

### 7. Build frontend for production

```powershell
cd frontend
npm run build
```

---

## Project Structure

```
mechacode-guardian/
├── frontend/               # React 19 + Vite + TypeScript
│   └── src/
│       ├── api/            # Typed fetch client → FastAPI backend
│       ├── components/     # SymptomForm, DiagnosisResult, EscalationNotice, Checklist, ReportDownload
│       ├── pages/          # DiagnosisPage (primary user journey)
│       └── i18n/           # Bahasa Indonesia + English translations
├── backend/
│   ├── api/                # FastAPI routers + Pydantic schemas
│   ├── core/               # Config, logging, domain models, EmbeddingConfig
│   ├── generation/         # LLM provider abstraction (Granite + Gemini)
│   ├── ingestion/          # IBM Docling parser + chunker (Day 2)
│   ├── retrieval/          # Astra DB ANN search client (Day 3)
│   ├── safety/             # Safety gate — keyword trigger matching (Day 4)
│   └── reporting/          # Markdown report assembler (Day 6)
├── scripts/
│   └── ingest.py           # CLI ingestion script (Day 2–3)
├── data/
│   └── safety_triggers.json  # 21 safety patterns — version-controlled, auditable (SR-07)
├── knowledge/
│   └── synthetic/          # Original synthetic mechatronics documentation
├── tests/
│   ├── unit/               # pytest unit tests
│   ├── integration/        # Integration tests (Day 6)
│   └── evaluation/         # 30-case evaluation dataset (Day 9)
├── docs/                   # Planning documents
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DELIVERY_PLAN.md
│   ├── EVALUATION_PLAN.md
│   ├── COMPETITION_REQUIREMENTS.md
│   └── IBM_BOB_USAGE.md
├── .env.example            # Variable names only — no real values
└── README.md
```

---

## Safety

MechaCode Guardian operates in an industrial context. The safety gate is deterministic and runs before any LLM call. All outputs carry the disclaimer: *"This is an AI-assisted recommendation. Always verify with the applicable technical manual and qualified personnel."*

See [`data/safety_triggers.json`](data/safety_triggers.json) for the version-controlled safety trigger list.

---

## Current Implementation Status

| Component | Status |
|---|---|
| Backend scaffold (FastAPI, routers, schemas) | ✅ Foundation |
| Frontend scaffold (React, components, i18n) | ✅ Foundation |
| Safety triggers list (21 patterns) | ✅ Done |
| Document ingestion pipeline — dry-run | ✅ Done (Day 2) |
| Manifest loading and validation | ✅ Done (Day 2) |
| Secure path validation (anti-traversal) | ✅ Done (Day 2) |
| Heading-aware chunker | ✅ Done (Day 2) |
| Deterministic metadata / chunk IDs | ✅ Done (Day 2) |
| Dry-run summary report | ✅ Done (Day 2) |
| Astra DB retrieval client | ⬜ Day 3 |
| Safety gate implementation | ⬜ Day 4 |
| LLM provider abstraction | ⬜ Day 5 |
| API endpoints (full pipeline) | ⬜ Day 6 |
| Evaluation dataset | ⬜ Day 9 |

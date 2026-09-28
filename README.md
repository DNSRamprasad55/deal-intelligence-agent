# Deal Intelligence Agent

**Deal Intelligence Agent** is an evidence-driven AI sales intelligence platform powered by **Hindsight Cloud** as its central persistent agent memory system.

Instead of treating LLM recommendations as one-off, stateless prompts, the Deal Intelligence Agent establishes a continuous closed-loop learning feedback system:

$$\text{RETAIN} \longrightarrow \text{RECALL} \longrightarrow \text{REFLECT} \longrightarrow \text{RECOMMEND} \longrightarrow \text{HUMAN DECISION} \longrightarrow \text{ACTION} \longrightarrow \text{OUTCOME} \longrightarrow \text{RETAIN}$$

---

## 💡 Problem & Solution

### The Problem
Sales organizations lose invaluable experience when deals close. When a deal is lost due to migration timeline concerns or won by offering a phased rollout workshop, that experience remains trapped in individual heads or buried in unstructured notes. Next time a similar objection arises in another deal, reps start from scratch.

### The Solution
The **Deal Intelligence Agent** automatically captures customer interactions, objections, requirements, and competitor mentions into **Hindsight Cloud**. When analyzing a new deal, the agent:
1. **Recalls** historical WON & LOST deal experiences relevant to the current situation.
2. **Reflects** over recalled evidence using structured multi-arm reasoning.
3. Generates evidence-backed **Recommendations** for the sales team.
4. Captures **Human-in-the-Loop** decisions (`ACCEPTED` / `REJECTED`).
5. Tracks executed **Actions** and real-world **Outcomes** (`POSITIVE`, `NEGATIVE`, `NEUTRAL`).
6. **Retains** the outcome experience back into Hindsight Cloud, enabling the agent to **learn from its own recommendations and their real-world results**.

---

## ⚡ Key Features

- **Real Hindsight Cloud Integration**: Uses the official `hindsight-client` Python SDK (v0.10.1) connecting to `deal-intelligence-global` memory bank.
- **Closed-Loop Memory System**: Closed feedback retention loop feeding recommendation outcomes back into persistent memory.
- **Evidence-Backed Guidance**: Synthesizes deal recommendations directly tied to historical WON/LOST evidence cards with contextual badges.
- **Human-in-the-Loop Control**: Sales reps explicitly review, accept, or reject recommendations and record actual deal outcomes.
- **Strict Architecture Decoupling**: Relational CRM business data is managed in PostgreSQL; experiential agent memory is managed in Hindsight Cloud.
- **Graceful Error Resilience**: If Hindsight Cloud is unavailable or out of credits, PostgreSQL transactional operations succeed safely without 500 errors or fake memory generation.

---

## 🏗️ Technology Stack

- **Frontend**: React 18, Vite, TypeScript (Strict Mode), Tailwind CSS, Lucide React, Axios
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Passlib/Bcrypt, PyJWT, HTTPX
- **Agent Memory**: Hindsight Cloud SDK (`hindsight-client` 0.10.1)
- **Database**: PostgreSQL 16 (production) / SQLite (development fallback)
- **LLM Provider**: Gemini API / OpenAI API (Provider Abstraction)
- **DevOps**: Docker, Docker Compose, Pytest, ESLint

---

## 📁 Project Structure

```text
deal-intelligence-agent/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routes (auth, deals, interactions, intelligence)
│   │   ├── core/            # Configuration, logging, security, JWT
│   │   ├── db/              # SQLAlchemy database engine & session handlers
│   │   ├── models/          # Relational ORM models (User, Company, Deal, Interaction, Recommendation, DealAction, DealOutcome)
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   └── services/        # Service layer (hindsight, recall, analysis, llm)
│   ├── alembic/             # Database schema migrations
│   ├── scripts/             # Live Hindsight Cloud verification scripts (Phases 2-5)
│   ├── tests/               # Pytest unit & integration test suites
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (Card, Badge, Button, Modal, Input, Select, etc.)
│   │   ├── context/         # AuthContext & state management
│   │   ├── pages/           # Dashboard, DealListPage, DealDetailPage, LoginPage
│   │   ├── services/        # API client abstractions (auth, deals, interactions, intelligence)
│   │   └── types/           # TypeScript interfaces
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Architecture & Hindsight memory documentation
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation Instructions

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ & npm
- PostgreSQL 16 (Optional; SQLite fallback is supported automatically)

### 2. Environment Configuration
Copy the template `.env.example` to `.env` in the project root or backend directory:

```bash
cp .env.example backend/.env
```

Configure your environment variables:
```env
DATABASE_URL=sqlite:///./deal_intelligence.db
HINDSIGHT_API_KEY=your_hindsight_api_key_here
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=deal-intelligence-global
LLM_API_KEY=your_llm_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
JWT_SECRET=super_secret_jwt_key_change_me_in_production_32_bytes_min
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

# Run Alembic migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

The API docs will be available at `http://localhost:8000/api/docs`.

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend dashboard will be available at `http://localhost:3000`.

---

## 🐳 Running with Docker Compose

To spin up PostgreSQL, the FastAPI backend, and the React frontend simultaneously:

```bash
docker compose up --build
```

---

## 🧪 Testing & Verification

### Unit Test Suite
Execute the full backend Pytest suite (22 unit tests):

```bash
cd backend
.venv\Scripts\python -m pytest -v
```

### Frontend Code Quality & Build
```bash
cd frontend
npm.cmd run lint
npm.cmd run build
```

### Live Hindsight Cloud Verification Scripts
```bash
cd backend

# Phase 2 — Real Hindsight RETAIN Verification
.venv\Scripts\python scripts/verify_hindsight_integration.py

# Phase 4 — Real Hindsight REFLECT Verification
.venv\Scripts\python scripts/verify_phase4_reflect.py

# Phase 5 — Closed Learning Loop Verification
.venv\Scripts\python scripts/verify_phase5_learning.py
```

---

## ⚠️ Known Limitations & Hindsight Cloud Credits Note

> [!NOTE]
> **Hindsight Cloud Credits & Rate Limits**: Live `RECALL`, `REFLECT`, and `RETAIN` requests against `https://api.hindsight.vectorize.io` require an active Hindsight Cloud API key with available credits. If Hindsight Cloud returns `402 Payment Required` (insufficient credits) or is offline, the Deal Intelligence Agent's PostgreSQL database, application state, and UI will continue to operate safely without crashing or throwing 500 errors.

---

## 📖 Additional Documentation

- [Architecture Overview](docs/architecture.md)
- [Hindsight Memory Model Documentation](docs/hindsight.md)

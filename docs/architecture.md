# Deal Intelligence Agent — Architecture Documentation

## 1. Executive Summary

The **Deal Intelligence Agent** is an evidence-driven sales intelligence system that bridges relational CRM transactional data (PostgreSQL) with persistent agent experience memory (**Hindsight Cloud**).

Rather than treating LLM recommendations as one-off stateless prompts, the agent maintains a continuous learning feedback loop:

$$\text{RETAIN} \longrightarrow \text{RECALL} \longrightarrow \text{REFLECT} \longrightarrow \text{RECOMMEND} \longrightarrow \text{HUMAN DECISION} \longrightarrow \text{ACTION} \longrightarrow \text{OUTCOME} \longrightarrow \text{RETAIN}$$

---

## 2. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (React + TypeScript + Vite + Tailwind)"]
        UI["SaaS Dashboard & Deal Detail View"]
        LoopUI["Closed Learning Loop Component"]
    end

    subgraph Backend ["Backend API (FastAPI + SQLAlchemy + Pydantic v2)"]
        Auth["JWT Auth & Route Controllers"]
        RecallService["DealRecallService"]
        AnalysisService["DealAnalysisService (Reflect)"]
        HindsightService["HindsightService (SDK Wrapper)"]
    end

    subgraph Storage ["Persistent Storage Layers"]
        PG[("PostgreSQL DB / SQLite Fallback\n(Transactional Deals, Actions, Outcomes)")]
        HindsightCloud[("Hindsight Cloud Memory Bank\n(deal-intelligence-global)")]
    end

    UI -->|REST API Requests| Auth
    Auth -->|CRUD Operations| PG
    Auth --> RecallService
    Auth --> AnalysisService
    RecallService -->|1. RECALL Memories| HindsightService
    AnalysisService -->|2. REFLECT Reasoning| HindsightService
    HindsightService <-->|Official Python SDK| HindsightCloud
    AnalysisService -->|3. Save Recommendation & Action| PG
    Auth -->|4. Record Outcome| AnalysisService
    AnalysisService -->|5. RETAIN Outcome Experience| HindsightService
```

---

## 3. Data Layer Separation of Responsibilities

A core architectural principle of the Deal Intelligence Agent is the strict decoupling between **relational business state** and **agent experience memory**:

### 3.1. PostgreSQL / SQLite (Transactional Application State)
- **Identity & Security**: Users, password hashes, JWT authorization roles (`sales_rep`, `manager`, `admin`).
- **CRM Domain Entities**: Companies, Contacts, Deals, Stages (`DISCOVERY`, `QUALIFICATION`, `TECHNICAL_EVALUATION`, `PROPOSAL`, `NEGOTIATION`, `CLOSED_WON`, `CLOSED_LOST`), Deal Values, Probabilities.
- **Activity Records**: Interactions (Calls, Meetings, Emails, Internal Notes, Demos, Technical Reviews).
- **Human-in-the-Loop State**: Persisted `Recommendation` records (Status: `PENDING`, `ACCEPTED`, `REJECTED`), `DealAction` execution records, and `DealOutcome` results (`POSITIVE`, `NEGATIVE`, `NEUTRAL`, `UNKNOWN`).

### 3.2. Hindsight Cloud (Persistent Agent Memory & Experience)
- **Memory Retention**: Storing structured deal experiences dynamically tagged with `deal:<id>`, `company:<id>`, `stage:<stage>`, `type:outcome`, `type:action`, `outcome:<type>`.
- **Semantic & Multi-Arm Recall**: Searching past won/lost deal experiences using BM25 keyword matching, vector embeddings, entity graphs, and temporal proximity.
- **Synthesized Reflection**: Running Hindsight `REFLECT` reasoning over recalled evidence to detect cross-deal patterns, identified risks, and next-action recommendations.

---

## 4. The Closed Learning Loop Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Sales Rep
    participant FE as React Frontend
    participant BE as FastAPI Backend
    participant DB as PostgreSQL
    participant HS as Hindsight Cloud

    User->>FE: Click "Analyze Deal Intelligence"
    FE->>BE: POST /api/deals/{id}/intelligence/analyze
    BE->>HS: RECALL historical deal evidence
    HS-->>BE: Recalled WON & LOST experiences
    BE->>HS: REFLECT reasoning over context & evidence
    HS-->>BE: Structured reasoning output
    BE->>DB: Save Recommendation (PENDING)
    BE-->>FE: Return DealAnalysisResponse
    FE->>User: Render Recommendation, Reasoning, Evidence Cards

    User->>FE: Click [Accept Recommendation]
    FE->>BE: POST /api/recommendations/{id}/action (ACCEPTED)
    BE->>DB: Save DealAction (COMPLETED) & Update Recommendation
    BE-->>FE: Return RecommendationResponse + action_id

    User->>FE: Fill Outcome Form & Click [Save Outcome]
    FE->>BE: POST /api/actions/{action_id}/outcome
    BE->>DB: Save DealOutcome record
    BE->>HS: RETAIN Outcome experience in bank "deal-intelligence-global"
    HS-->>BE: Memory retained (memory_id)
    BE-->>FE: Return OutcomeResponse with hindsight.status="stored"
    FE->>User: Display "✓ Learned by Hindsight" status banner
```

---

## 5. Resilience & Error Handling Architecture

The application is engineered with high resilience:
1. **Graceful Memory Fallback**: If Hindsight Cloud credentials are unconfigured or Hindsight Cloud returns `402 Payment Required` (insufficient credits), PostgreSQL transactional operations (actions, outcomes, deal creation) succeed cleanly.
2. **Safe API Responses**: Status messages clearly indicate `hindsight.status="unavailable"` or `hindsight.status="not_configured"` without throwing 500 errors or returning fake data.
3. **Async Event Loop Safety**: All Hindsight SDK calls use native `a`-prefixed async methods (`aget_version`, `acreate_bank`, `aretain`, `arecall`, `areflect`), avoiding nested event loop execution (`asyncio.run` conflicts).

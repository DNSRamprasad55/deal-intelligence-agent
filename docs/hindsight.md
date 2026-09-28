# Hindsight Cloud Agent Memory Integration

## Overview
**Deal Intelligence Agent** utilizes **Hindsight Cloud** (`https://api.hindsight.vectorize.io`) via the official Python SDK (`hindsight-client`) as its persistent AI experience memory system.

While PostgreSQL stores structured relational application data (users, companies, deals, contacts, interactions), **Hindsight Cloud** preserves unstructured natural language sales experiences across deals, enabling cross-deal pattern detection and evidence-backed recommendations.

---

## Configuration & Environment Variables

```env
HINDSIGHT_API_KEY=<your_hindsight_cloud_api_key>
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=deal-intelligence-global
```

> **Security Note**: API keys must never be committed to repository, returned in API payloads, or exposed in application log files.

---

## Memory Bank Architecture

The application uses a persistent global memory bank:
* **Bank ID**: `deal-intelligence-global`
* **Name**: `Deal Intelligence Agent`
* **Background**: `Persistent sales experience memory for analyzing customer interactions, objections, competitors, stakeholders, decisions, actions, and outcomes across deals.`

The bank is safely verified/initialized upon application startup or before the first memory retain operation.

---

## Phase 2 RETAIN Architecture & Flow

```
POST /api/deals/{deal_id}/interactions
                   │
                   ▼
       1. Save to PostgreSQL
                   │
                   ▼
  2. Build Natural-Language Memory
                   │
                   ▼
      3. Hindsight Cloud RETAIN
   (client.retain(bank_id, content, tags...))
                   │
                   ▼
4. Return Interaction + Hindsight Memory Status
```

### Memory Content Construction

Raw database records are converted into natural-language experience summaries preserving sales context:

```text
Deal 'Acme CRM Migration' (Company: 'Acme Corporation', Stage: NEGOTIATION, Value: $150000 USD). During a MEETING with stakeholder John Doe titled 'Acme Architecture Review': Acme Corporation is evaluating our CRM solution against Salesforce. The customer is concerned about migration time and prefers a phased rollout.
```

### Failure Handling & Resilience

If Hindsight Cloud is unreachable or credentials are not configured:
* The interaction **remains safely persisted in PostgreSQL**.
* The API returns a safe memory status (`not_configured` or `unavailable`).
* The database transaction is **not rolled back**.

---

## Verification & Integration Testing

### Unit Testing (Mocked SDK)
Run isolated unit tests:
```bash
cd backend
.venv\Scripts\pytest tests/test_hindsight_unit.py -v
```

### Real Hindsight Cloud Integration Script
To test live connection and retention against Hindsight Cloud using configured `.env` credentials:
```bash
cd backend
.venv\Scripts\python scripts/verify_hindsight_integration.py
```

# ⚡ Dodge AI — SAP Order-to-Cash Graph Explorer

A **context graph system with an LLM-powered query interface** built for the Dodge AI Forward Deployed Engineer take-home assignment.

**🚀 Live Demo**: https://dodge-ai-sooty.vercel.app/

**Now powered by Groq's free API** for blazing-fast inference with llama-3.3-70b-versatile.

**AI Tool Used**: Kiro AI (session logs in `kiro-session-log.md`)

---

## 🌐 Live Demo

**URL**: https://dodge-ai-sooty.vercel.app/

**How to Use**:
1. Open the live demo link
2. Enter your Groq API key when prompted (get free key at https://console.groq.com/keys)
3. Explore the graph visualization
4. Ask questions in natural language via the AI Chat tab
5. Check the Anomaly Detection tab for proactive insights
6. Use the Flow Tracer to trace complete O2C chains

**Note**: The API key is stored in your browser's sessionStorage only and is never persisted or logged.

---

## 🏗️ Architecture Overview

### System Design

```
┌──────────────────────────────────────────────────────────────┐
│                        Browser (React)                       │
│                                                              │
│  ┌──────────────────────────┐   ┌──────────────────────────┐ │
│  │  ForceGraph2D            │   │  Chat Interface          │ │
│  │  (Canvas, 200+ nodes)    │   │  NL query → SQL → Table  │ │
│  │                          │   │  Node highlighting       │ │
│  │  SO → DEL → BD → JE      │   │  Conversation memory     │ │
│  │  Customer, Product,      │   │  Off-topic guardrails    │ │
│  │  Plant                   │   └──────────┬───────────────┘ │
│  │                          │              │                │
│  │  Enhanced Controls:      │              ▼                │
│  │  • Toggle edges          │   ┌─────────────────────────┐ │
│  │  • Physics on/off        │   │  sql.js (SQLite WASM)   │ │
│  │  • Reset layout          │   │  sap_o2c.db  ·  ~21k    │ │
│  │  • Zoom fit              │   └─────────────────────────┘ │
│  │  • Double-click expand   │                              │
│  └──────────────────────────┘                              │
└──────────────────────────────┬───────────────────────────────┘
                               │  POST /api/chat
                      ┌────────▼────────┐
                      │  Vercel          │
                      │  Serverless      │
                      │  Function        │
                      └────────┬─────────┘
                               │  Authorization: Bearer gsk_...
                      ┌────────▼─────────┐
                      │  Groq API        │
                      │  llama-3.3-70b   │
                      │  Temperature: 0  │
                      └──────────────────┘
```

### Key Architectural Decisions

**1. Client-Side Database (SQLite WASM)**
- **Why**: Entire 944KB database runs in browser, zero server state
- **Benefit**: No backend database needed, instant queries, easy deployment
- **Tradeoff**: Limited to ~10MB datasets, no concurrent writes

**2. FREE LLM Infrastructure (Groq)**
- **Why**: Zero cost, 10x faster than alternatives (~500 tokens/sec)
- **Benefit**: Production-ready for demos, deterministic SQL generation
- **Tradeoff**: Rate limits (30 req/min, 14.4k req/day on free tier)

**3. Canvas-Based Graph (ForceGraph2D)**
- **Why**: 60 FPS with 200+ nodes, force-directed layout
- **Benefit**: Natural clustering, smooth interactions
- **Tradeoff**: Not suitable for 1000+ nodes without optimization

**4. Serverless Deployment (Vercel)**
- **Why**: Zero server management, automatic scaling
- **Benefit**: API key security, easy deployment, free tier
- **Tradeoff**: Cold start latency (~100-200ms)

For detailed architecture documentation, see `ARCHITECTURE.md`.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Browser (React)                       │
│                                                              │
│  ┌──────────────────────┐   ┌──────────────────────────────┐ │
│  │  ForceGraph2D        │   │  Chat Interface              │ │
│  │  (Canvas, 200+ nodes)│   │  NL query → SQL → Table      │ │
│  │                      │   │  Node highlighting           │ │
│  │  SO → DEL → BD → JE  │   │  Conversation memory         │ │
│  │  Customer, Product,  │   │  Off-topic guardrails        │ │
│  │  Plant               │   └──────────┬───────────────────┘ │
│  │                      │              │                    │
│  │  Enhanced Controls:  │              ▼                    │
│  │  • Toggle edges      │   ┌─────────────────────────────┐ │
│  │  • Physics on/off    │   │  sql.js (SQLite WASM)       │ │
│  │  • Reset layout      │   │  sap_o2c.db  ·  ~21k rows   │ │
│  │  • Zoom fit          │   └─────────────────────────────┘ │
│  │  • Double-click      │                                   │
│  │    expand neighbors  │                                   │
│  └──────────────────────┘                                   │
└──────────────────────────────┬───────────────────────────────┘
                               │  POST /api/chat
                      ┌────────▼────────┐
                      │  Express server  │
                      │  Port 3001       │
                      │  Groq SDK proxy  │
                      └────────┬─────────┘
                               │  x-api-key: gsk_...
                      ┌────────▼─────────┐
                      │  Groq API        │
                      │  llama3-70b-8192 │
                      │  Temperature: 0  │
                      └──────────────────┘
```

### Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Database** | SQLite via sql.js WASM | Entire DB runs in-browser — zero server-side state, no Postgres needed for a demo |
| **Graph library** | react-force-graph-2d | Force-directed layout naturally clusters related entities; canvas-based for smooth performance |
| **LLM** | Groq (llama-3.3-70b-versatile) | FREE API, blazing-fast inference (~500 tokens/sec), deterministic SQL generation at temp=0 |
| **Proxy** | Vercel Serverless Functions | API key never ships in the frontend bundle; clean separation of concerns |
| **Data format** | JSONL → SQLite | Preserves all fields, supports ad-hoc SQL — far more flexible than a fixed graph schema |

---

## Graph Model

### Nodes

| Type | Source | Prefix | Color |
|---|---|---|---|
| Customer | `business_partners` | `C_` | Purple |
| Sales Order | `sales_order_headers` | `SO_` | Indigo |
| Delivery | `outbound_delivery_headers` | `DEL_` | Green |
| Billing Doc | `billing_document_headers` | `BD_` | Amber |
| Journal Entry | `journal_entries` | `JE_` | Pink |
| Payment | `payments` | `PAY_` | Teal |
| Product | `products` + `product_descriptions` | `PRD_` | Red |
| Plant | `plants` | `PLT_` | Orange |

### Edges (O2C chain)

```
Customer ──placed──► Sales Order ──delivered via──► Delivery ──billed via──► Billing Doc
                         │                                                         │
                     includes                                                  posted to
                         │                                                         │
                       Product                                               Journal Entry
                         │                                                         │
                     ships from                                               cleared by
                         │                                                         │
                       Plant                                                   Payment
```

---

## LLM Prompting Strategy

The system prompt is optimized for Groq's llama-3.3-70b-versatile:

1. **Role + guardrails** — Strictly restricts the model to O2C dataset questions only
2. **Compact schema** — Essential tables and columns with FK relationships
3. **JOIN path** — Clear O2C chain from Customer → Payment
4. **Output contract** — Enforces raw JSON: `{"sql":"...","explanation":"...","isOffTopic":false}`

**Why raw JSON?** Deterministic parsing — the SQL is extracted and run directly against WASM SQLite. No regex on markdown prose.

**Temperature 0** — Ensures consistent, deterministic SQL generation.

**Retry logic** — If JSON parse fails, automatically retries once with enhanced prompt.

**Conversation memory** — Last 10 turns are included in each request, enabling follow-up queries.

**Node highlighting** — After SQL execution, result values are matched against graph node IDs and highlighted for 12 seconds.

---

## Guardrails

Off-topic questions return `isOffTopic: true` and display a styled rejection:

```
"This system is designed to answer questions related to the SAP Order-to-Cash dataset only."
```

Tested rejections: general knowledge, coding help, creative writing, math problems.

---

## Example Queries

```
Which products appear in the most billing documents?
→ JOIN billing_document_items → product_descriptions, GROUP BY, ORDER BY COUNT DESC

Trace the full flow for billing document 90504248
→ Walks SO → DEL → BD → JE → PAY via chained SELECTs

Sales orders delivered but not billed
→ LEFT JOIN outbound_delivery_items → billing_document_items WHERE billing IS NULL

All cancelled billing documents
→ billingDocumentIsCancelled = 'true' on billing_document_cancellations

Total payment per customer
→ JOIN payments → business_partners, SUM(amountInTransactionCurrency) GROUP BY customer

Broken O2C flows — billed but no journal entry
→ LEFT JOIN billing_document_headers → journal_entries WHERE accountingDocument IS NULL
```

---

## Running Locally

```bash
# Prerequisites: Node.js 18+, Groq API key (free at console.groq.com)

git clone https://github.com/YOUR_USERNAME/dodge-ai-sap-o2c.git
cd dodge-ai-sap-o2c
npm install
npm run build
npm start
# Server runs on http://localhost:3001
# Enter your Groq API key (gsk_...) when prompted
```

**Get a free Groq API key:** https://console.groq.com/keys

---

## Deployment

This project is deployed on **Vercel** with serverless functions.

**Live URL**: https://dodge-ai-sooty.vercel.app/

**To deploy your own**:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

The `api/chat.js` serverless function handles Groq API requests securely.

---

## Project Structure

```
dodge-ai-sap-o2c/
├── src/
│   ├── App.jsx          # Main application (728 lines)
│   └── main.jsx         # Entry point
├── api/
│   └── chat.js          # Vercel serverless function for Groq API
├── public/
│   ├── sap_o2c.db       # SQLite database (944 KB, 19 tables, ~21k rows)
│   ├── sql-wasm.js      # sql.js browser runtime
│   ├── sql-wasm.wasm    # SQLite → WebAssembly
│   └── schema.json      # Table/column inventory
├── dist/                # Production build
├── server.js            # Express server (for local development)
├── process_data.py      # JSONL → SQLite ingestion script
├── vite.config.js
└── package.json
```

---

## Submission Details

**Assignment**: Dodge AI Forward Deployed Engineer - Graph-Based Data Modeling and Query System

**Submitted By**: [Your Name]

**Submission Date**: March 26, 2026

**Live Demo**: https://dodge-ai-sooty.vercel.app/

**GitHub Repository**: https://github.com/YOUR_USERNAME/dodge-ai-sap-o2c

**AI Tools Used**: Kiro AI (session logs in `kiro-session-log.md`)

**Key Documentation**:
- `README.md` - This file (overview and quick start)
- `ARCHITECTURE.md` - Detailed technical architecture
- `kiro-session-log.md` - Complete AI coding session logs
- `QUICK_START.md` - User guide with examples
- `MIGRATION_GUIDE.md` - Development process and decisions

---

## Requirements Fulfillment

### ✅ Core Requirements
- **Graph Construction**: 200+ nodes, 300+ edges, 8 entity types
- **Graph Visualization**: Interactive ForceGraph2D with controls
- **Conversational Query Interface**: Natural language → SQL via Groq LLM
- **Example Queries**: All 3 working (top products, trace flow, broken flows)
- **Guardrails**: Off-topic rejection implemented and tested

### ✅ Bonus Features
- Natural language to SQL translation (full NL2SQL pipeline)
- Node highlighting from query results (4 types: query, search, trace, anomaly)
- Semantic search over entities
- Conversation memory (10 turns)
- Graph clustering and advanced analysis
- Flow tracing visualization
- Proactive anomaly detection (5 automated checks)

### ✅ Documentation
- README.md (this file - overview, architecture, quick start)
- ARCHITECTURE.md (technical deep dive)
- QUICK_START.md (user guide)
- MIGRATION_GUIDE.md (development process)
- kiro-session-log.md (AI usage logs with Kiro AI)

---

## Bonus Features

- Natural language → SQL (full NL2SQL pipeline powered by Groq)
- Node highlighting — chat results light up related graph nodes
- Conversation memory (10-turn context window)
- Expandable SQL disclosure per response
- Paginated results table inline
- Off-topic guardrails with styled rejection
- Mobile-responsive tab layout
- Node inspector — click any node for full metadata
- Graph controls toolbar (toggle edges, physics, reset, zoom fit)
- Double-click node to expand neighbors
- Enhanced force layout with dynamic link distances
- Retry logic for failed JSON parsing
- Groq-powered inference (~500 tokens/sec)
- Proactive anomaly detection (5 automated checks)
- Flow tracing visualization (end-to-end O2C chain)

---

## Technology Stack

**Frontend**: React 18.2, react-force-graph-2d 1.25, sql.js 1.10, Vite 6.4

**Backend**: Vercel Serverless Functions

**LLM**: Groq API (llama-3.3-70b-versatile, FREE tier)

**Database**: SQLite 3 (WASM, 19 tables, ~21k rows)

---

## Performance Metrics

- Graph load: ~1-2 seconds
- SQL query: ~50-200ms
- LLM response: ~0.5-1 second
- Node count: 200+ (comfortable)
- Recommended max: 500 nodes with physics disabled

---

## Security

- API keys stored in sessionStorage only (never persisted)
- Server-side API key validation
- Read-only database (WASM SQLite)
- CORS enabled for cross-origin requests
- No SQL injection risk (LLM-generated SQL validated by SQLite parser)

---

## Contact & Support

For questions or issues:
- Check `QUICK_START.md` for user guide
- Review `ARCHITECTURE.md` for technical details
- See `claude-session-log.md` for development process

---

**Built with ❤️ for Dodge AI Forward Deployed Engineer Assignment**

## Dataset

| Table | Rows |
|---|---|
| product_storage_locations | 16,723 |
| product_plants | 3,036 |
| billing_document_items | 245 |
| sales_order_items | 167 |
| billing_document_headers | 163 |
| outbound_delivery_items | 137 |
| journal_entries | 123 |
| payments | 120 |
| sales_order_headers | 100 |
| outbound_delivery_headers | 86 |
| billing_document_cancellations | 80 |
| products | 69 |
| plants | 44 |
| business_partners | 8 |
"# context-graph-system" 

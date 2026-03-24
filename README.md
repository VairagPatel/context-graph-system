# Graph-Based Data Modeling and Query System

A full-stack application that transforms fragmented relational business data into a unified graph representation, enabling intuitive exploration through interactive visualization and natural language querying.

## Architecture Overview

The system consists of three primary layers:

1. **Data Layer**: Neo4j graph database storing business entities (Orders, Deliveries, Invoices, Payments, Customers, Products, Addresses) as nodes with typed relationships
2. **Backend Layer**: Python FastAPI service handling data import, query translation, and database operations
3. **Frontend Layer**: React + Vite application with React Flow visualization and conversational chat interface

### Key Features

- **Interactive Graph Visualization**: Explore business data relationships visually using React Flow
- **Natural Language Queries**: Ask questions in plain English, powered by LLM translation to Cypher
- **Data Import**: Upload CSV/JSON files to populate the graph database
- **Flow Tracing**: Track complete business process flows (Order → Delivery → Invoice → Payment)
- **Broken Flow Detection**: Identify incomplete processes and bottlenecks
- **Domain Guardrails**: Query validation ensures system is used for business intelligence purposes

### Technology Stack

**Backend**:
- Python 3.11+
- FastAPI (async web framework)
- Neo4j Python Driver (database connectivity)
- Pydantic (data validation)
- httpx (LLM API requests)

**Frontend**:
- React 18
- Vite (build tool)
- React Flow (graph visualization)
- Axios (HTTP client)
- TailwindCSS (styling)

**Database**:
- Neo4j 5.x (graph database)

**External Services**:
- Groq API or Google Gemini API (LLM provider)

## Prerequisites

Before setting up the system, ensure you have the following:

### Required Software
- **Python 3.11 or higher**: Backend runtime environment
  - Check version: `python --version` or `python3 --version`
  - Download from: [python.org](https://www.python.org/downloads/)
  
- **Node.js 18 or higher**: Frontend build tooling
  - Check version: `node --version`
  - Download from: [nodejs.org](https://nodejs.org/)
  - Includes npm package manager

### Required Services
- **Neo4j Aura Account**: Cloud-hosted graph database
  - Free tier available at [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/)
  - Provides 200k nodes and 400k relationships
  - No credit card required for free tier
  
- **LLM API Key**: Natural language query translation
  - **Option 1 - Groq (Recommended)**: Fast inference, generous free tier
    - Sign up at [console.groq.com](https://console.groq.com)
    - Free tier: 14,400 requests/day
  - **Option 2 - Google Gemini**: Google's LLM service
    - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    - Free tier: 60 requests/minute

### Optional Tools
- **Git**: For cloning the repository
- **Docker**: For containerized deployment (optional)
- **curl or Postman**: For API testing

## Setup Instructions

### Neo4j Database Setup

Before running the backend, set up your Neo4j database:

1. **Create Neo4j Aura Instance**:
   - Go to [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/)
   - Click "Start Free" and create an account
   - Click "Create Instance" and select "Free" tier
   - Choose a name for your instance (e.g., "graph-query-system")
   - Click "Create"

2. **Save Connection Credentials**:
   - **Connection URI**: Format is `neo4j+s://xxxxx.databases.neo4j.io`
   - **Username**: Default is `neo4j`
   - **Password**: Auto-generated password (save this immediately!)
   - Download the credentials file for safekeeping

3. **Verify Connection**:
   - Click "Open" to access Neo4j Browser
   - Run test query: `RETURN "Hello, Neo4j!" AS message`
   - If successful, your database is ready

### LLM API Key Setup

Choose one LLM provider:

#### Option 1: Groq (Recommended)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to "API Keys" section
4. Click "Create API Key"
5. Name your key (e.g., "graph-query-system")
6. Copy the API key (starts with `gsk_...`)
7. Save for use in backend `.env` file

#### Option 2: Google Gemini
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the API key
6. Save for use in backend `.env` file

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create and activate virtual environment**:

   **On macOS/Linux**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **On Windows**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   You should see `(venv)` in your terminal prompt.

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

   This installs:
   - FastAPI (web framework)
   - Uvicorn (ASGI server)
   - Neo4j Python Driver
   - Pydantic (data validation)
   - httpx (HTTP client for LLM APIs)
   - python-multipart (file uploads)
   - python-dotenv (environment variables)

4. **Create environment configuration**:
```bash
cp .env.example .env
```

5. **Configure environment variables** in `.env`:

   Open `.env` in a text editor and update:

   ```bash
   # Neo4j Database Configuration
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-neo4j-password

   # LLM Provider Configuration
   LLM_PROVIDER=groq  # or "gemini"
   LLM_API_KEY=your-api-key-here

   # API Configuration
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000

   # Server Configuration (optional)
   HOST=0.0.0.0
   PORT=8000
   ```

   **Important**:
   - Replace `your-instance.databases.neo4j.io` with your actual Neo4j URI
   - Replace `your-neo4j-password` with your Neo4j password
   - Replace `your-api-key-here` with your Groq or Gemini API key
   - Set `LLM_PROVIDER` to match your chosen provider

6. **Run the development server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

   **Flags explained**:
   - `--reload`: Auto-restart on code changes (development only)
   - `--host 0.0.0.0`: Accept connections from any network interface
   - `--port 8000`: Listen on port 8000

7. **Verify backend is running**:

   Open a browser or use curl:
   ```bash
   curl http://localhost:8000/api/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "neo4j_connected": true,
     "llm_provider": "groq"
   }
   ```

   If `neo4j_connected` is `false`, check your Neo4j credentials.

**API Documentation**: Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation (Swagger UI).

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

   This installs:
   - React 18 (UI framework)
   - Vite (build tool)
   - React Flow (graph visualization)
   - Axios (HTTP client)
   - TailwindCSS (styling)
   - TypeScript (type safety)

3. **Create environment configuration**:
```bash
cp .env.example .env
```

4. **Configure environment variables** in `.env`:

   Open `.env` in a text editor and update:

   ```bash
   # Backend API URL
   VITE_API_URL=http://localhost:8000
   ```

   **Important**:
   - Use `http://localhost:8000` for local development
   - No trailing slash
   - Must start with `VITE_` prefix for Vite to expose it

5. **Run the development server**:
```bash
npm run dev
```

   The server will start and display:
   ```
   VITE v5.x.x  ready in xxx ms

   ➜  Local:   http://localhost:5173/
   ➜  Network: use --host to expose
   ```

6. **Open the application**:

   Navigate to [http://localhost:5173](http://localhost:5173) in your browser.

   You should see:
   - Graph visualization on the left
   - Chat interface on the right
   - Empty graph (until you import data)

7. **Import sample data** (optional):

   Use the sample data files in the `data/` directory:
   ```bash
   # From the project root
   curl -X POST http://localhost:8000/api/import \
     -F "file=@data/customers.csv"
   ```

   Repeat for other CSV files (orders, deliveries, invoices, payments, products, addresses).

**Development Tools**:
- **Hot Module Replacement**: Changes to code automatically update in browser
- **TypeScript Checking**: Run `npm run type-check` to check for type errors
- **Linting**: Run `npm run lint` to check code style

## API Endpoints

### POST /api/query
Submit natural language queries and receive structured results.

**Request Body**:
```json
{
  "query": "Show me the top 10 products by order count",
  "conversation_id": "optional-session-id",
  "include_cypher": false
}
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "product_name": "Widget A",
      "product_id": "P001",
      "order_count": 45
    }
  ],
  "cypher": "MATCH (p:Product)<-[:CONTAINS]-(o:Order) RETURN p.name AS product_name, p.product_id, COUNT(o) AS order_count ORDER BY order_count DESC LIMIT 10",
  "node_ids": ["P001", "P002"]
}
```

**Status Codes**:
- `200 OK`: Query executed successfully
- `400 Bad Request`: Invalid query or out-of-domain
- `500 Internal Server Error`: Query execution failed

### GET /api/graph
Fetch graph data for visualization.

**Query Parameters**:
- `limit` (optional): Maximum number of nodes to return (default: 100)

**Response**:
```json
{
  "nodes": [
    {
      "id": "O001",
      "label": "Order",
      "properties": {
        "order_id": "O001",
        "customer_id": "C001",
        "order_date": "2024-01-15",
        "total_amount": 299.99,
        "status": "delivered"
      }
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "O001",
      "target": "D001",
      "type": "DELIVERED_BY",
      "properties": {}
    }
  ]
}
```

### POST /api/import
Upload business data files (CSV or JSON format).

**Request**: `multipart/form-data` with file attachment

**Response**:
```json
{
  "success": true,
  "nodes_created": 150,
  "relationships_created": 320,
  "errors": []
}
```

**Supported Entity Types**:
- Orders, Deliveries, Invoices, Payments, Customers, Products, Addresses

### GET /api/schema
Retrieve the graph schema definition.

**Response**:
```json
{
  "node_types": [
    {
      "label": "Order",
      "properties": ["order_id", "customer_id", "order_date", "total_amount", "status"]
    }
  ],
  "relationship_types": ["DELIVERED_BY", "BILLED_BY", "PAID_BY", "PURCHASED_BY", "SHIPS_TO", "CONTAINS"]
}
```

### GET /api/health
Check service health status.

**Response**:
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "llm_provider": "groq"
}
```

**Status Values**:
- `healthy`: All services operational
- `degraded`: Neo4j connection failed

## Deployment

### Deployment Overview

The system consists of three components that must be deployed:
1. **Neo4j Database**: Already hosted on Neo4j Aura (no deployment needed)
2. **Backend API**: Deploy to Render, Railway, or Docker
3. **Frontend Web App**: Deploy to Vercel, Netlify, or static hosting

**Recommended Stack**:
- Neo4j Aura (free tier)
- Render or Railway for backend (free tier)
- Vercel for frontend (free tier)

### Backend Deployment

#### Option 1: Render (Recommended)

Render provides free hosting for web services with automatic deployments from GitHub.

**Steps**:
1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Create Render account**:
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Create new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically

4. **Configure environment variables**:
   - In Render dashboard, go to "Environment"
   - Add the following variables:
     - `NEO4J_URI`: Your Neo4j Aura connection string
     - `NEO4J_USER`: `neo4j`
     - `NEO4J_PASSWORD`: Your Neo4j password
     - `LLM_PROVIDER`: `groq` or `gemini`
     - `LLM_API_KEY`: Your LLM API key
     - `CORS_ORIGINS`: Your frontend URL (e.g., `https://your-app.vercel.app`)

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Deployment takes 2-5 minutes

6. **Verify deployment**:
   - Copy your Render URL (e.g., `https://your-app.onrender.com`)
   - Visit `https://your-app.onrender.com/api/health`
   - Should return `{"status": "healthy", "neo4j_connected": true}`

**Notes**:
- Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Automatic deployments on git push

#### Option 2: Railway

Railway offers simple deployment with automatic HTTPS and environment management.

**Steps**:
1. **Prepare Railway configuration**:
   ```bash
   cd backend
   mv railway.txt railway.json
   ```

2. **Create Railway account**:
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

3. **Create new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

4. **Configure environment variables**:
   - In Railway dashboard, go to "Variables"
   - Add the same variables as Render (see above)
   - Railway automatically sets `PORT` variable

5. **Deploy**:
   - Railway automatically builds using Dockerfile
   - Deployment takes 2-5 minutes
   - Copy your Railway URL (e.g., `https://your-app.up.railway.app`)

6. **Verify deployment**:
   - Visit `https://your-app.up.railway.app/api/health`

**Notes**:
- Free tier: $5 credit per month
- No automatic spin-down
- Faster cold starts than Render

#### Option 3: Docker (Self-Hosted)

Deploy to any server with Docker installed (VPS, AWS EC2, DigitalOcean, etc.).

**Steps**:
1. **Build Docker image**:
   ```bash
   cd backend
   docker build -t graph-query-backend .
   ```

2. **Run container**:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e NEO4J_URI="neo4j+s://your-instance.databases.neo4j.io" \
     -e NEO4J_USER="neo4j" \
     -e NEO4J_PASSWORD="your-password" \
     -e LLM_PROVIDER="groq" \
     -e LLM_API_KEY="your-api-key" \
     -e CORS_ORIGINS="https://your-frontend-domain.com" \
     --name graph-query-backend \
     --restart unless-stopped \
     graph-query-backend
   ```

3. **Verify deployment**:
   ```bash
   curl http://localhost:8000/api/health
   ```

4. **Set up reverse proxy** (optional but recommended):
   - Use Nginx or Caddy for HTTPS
   - Example Nginx config:
     ```nginx
     server {
         listen 80;
         server_name api.yourdomain.com;
         
         location / {
             proxy_pass http://localhost:8000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
     }
     ```

**Detailed backend deployment guide**: See [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md)

### Frontend Deployment

#### Option 1: Vercel (Recommended)

Vercel provides optimized hosting for React applications with automatic deployments.

**Steps**:
1. **Create Vercel account**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import project**:
   - Click "New Project"
   - Import your GitHub repository
   - Set **Root Directory** to `frontend`
   - Vercel auto-detects Vite configuration

3. **Configure environment variables**:
   - In project settings, go to "Environment Variables"
   - Add: `VITE_API_URL` = `https://your-backend.onrender.com`
   - **Important**: Use your actual backend URL (no trailing slash)

4. **Deploy**:
   - Click "Deploy"
   - Deployment takes 1-2 minutes
   - Copy your Vercel URL (e.g., `https://your-app.vercel.app`)

5. **Update backend CORS**:
   - Go to your backend deployment (Render/Railway)
   - Update `CORS_ORIGINS` environment variable
   - Add your Vercel URL: `https://your-app.vercel.app`
   - Redeploy backend if needed

6. **Verify deployment**:
   - Visit your Vercel URL
   - Open browser DevTools (F12) → Console
   - Check for CORS errors (should be none)
   - Try submitting a query in the chat interface

**Notes**:
- Automatic deployments on git push
- Preview deployments for pull requests
- Global CDN for fast loading
- Free tier: Unlimited personal projects

#### Option 2: Netlify

Netlify offers similar features to Vercel with a different interface.

**Steps**:
1. **Create Netlify account**:
   - Go to [netlify.com](https://netlify.com)
   - Sign up with GitHub

2. **Create new site**:
   - Click "Add new site" → "Import an existing project"
   - Connect to GitHub and select your repository

3. **Configure build settings**:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

4. **Configure environment variables**:
   - In site settings, go to "Environment variables"
   - Add: `VITE_API_URL` = `https://your-backend.onrender.com`

5. **Deploy**:
   - Click "Deploy site"
   - Copy your Netlify URL (e.g., `https://your-app.netlify.app`)

6. **Update backend CORS** (same as Vercel steps above)

#### Option 3: Static Hosting (Self-Hosted)

Deploy to any static file server (Nginx, Apache, S3, etc.).

**Steps**:
1. **Build production bundle**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Configure environment variables**:
   - Create `.env.production` before building:
     ```bash
     VITE_API_URL=https://your-backend-url.com
     ```
   - Rebuild: `npm run build`

3. **Deploy `dist` directory**:
   - The `dist` directory contains all static files
   - Upload to your web server

4. **Example: Nginx configuration**:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       root /var/www/graph-query-frontend/dist;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

5. **Example: Python HTTP server** (testing only):
   ```bash
   cd dist
   python -m http.server 8080
   ```

**Detailed frontend deployment guide**: See [frontend/DEPLOYMENT.md](frontend/DEPLOYMENT.md)

### Post-Deployment Checklist

After deploying both frontend and backend:

- [ ] **Backend health check passes**: Visit `https://your-backend/api/health`
- [ ] **Frontend loads**: Visit your frontend URL
- [ ] **CORS configured**: Backend `CORS_ORIGINS` includes frontend URL
- [ ] **API connection works**: Submit a test query in chat interface
- [ ] **No console errors**: Check browser DevTools console
- [ ] **Neo4j connected**: Health check shows `neo4j_connected: true`
- [ ] **LLM configured**: Health check shows correct `llm_provider`
- [ ] **Data imported**: Import sample data via `/api/import` endpoint

### Troubleshooting Deployment

**Backend Issues**:
- **Health check fails**: Verify Neo4j credentials and network access
- **LLM errors**: Check API key and provider setting
- **CORS errors**: Ensure `CORS_ORIGINS` includes frontend URL

**Frontend Issues**:
- **Blank page**: Check browser console for errors
- **API requests fail**: Verify `VITE_API_URL` is correct
- **Build fails**: Check Node.js version (requires 18+)

**Connection Issues**:
- **CORS errors**: Update backend `CORS_ORIGINS` and redeploy
- **Timeout errors**: Check backend is running and accessible
- **SSL errors**: Ensure both frontend and backend use HTTPS in production

## Design Decisions and Architecture

### Graph Modeling Approach

The system uses a **property graph model** where business entities are represented as nodes with properties, and relationships between entities are represented as typed edges. This design choice was made for several key reasons:

**Why Property Graphs?**
- **Efficient Traversal**: Graph databases excel at relationship queries. Finding "all orders for a customer with their deliveries and invoices" requires a single traversal operation, whereas SQL would need multiple joins.
- **Flexible Schema**: Adding new entity types or relationships doesn't require schema migrations or data restructuring.
- **Natural Representation**: Business processes are inherently graph-like (Order → Delivery → Invoice → Payment), making the model intuitive.
- **Many-to-Many Relationships**: Orders containing multiple Products are naturally represented without junction tables.

**Schema Design Principles**:
- Each business entity (Order, Delivery, Invoice, Payment, Customer, Product, Address) is a distinct node type
- Relationships are typed and directional (e.g., `DELIVERED_BY`, `BILLED_BY`, `PAID_BY`)
- Properties are stored directly on nodes (no separate property tables)
- Foreign keys from relational data become graph edges during import

**Example Flow**:
```
(Order)-[:PURCHASED_BY]->(Customer)
(Order)-[:DELIVERED_BY]->(Delivery)
(Order)-[:BILLED_BY]->(Invoice)
(Invoice)-[:PAID_BY]->(Payment)
(Order)-[:CONTAINS {quantity: 2}]->(Product)
```

### LLM Prompting Strategy

The query translator uses **few-shot prompting** to convert natural language to Cypher queries. This approach was chosen over fine-tuning or RAG for several reasons:

**Why Few-Shot Prompting?**
- **Cost-Effective**: Works with free-tier LLM providers (Groq, Gemini)
- **No Training Required**: No need for labeled datasets or model fine-tuning
- **Adaptable**: Easy to add new examples or modify schema context
- **Transparent**: Prompt engineering is visible and debuggable

**Prompt Structure**:
1. **Schema Context**: Complete graph schema with node types, properties, and relationship types
2. **Few-Shot Examples**: 8-10 example query translations covering:
   - Product analysis ("Show me top products by order count")
   - Flow tracing ("Trace the complete flow for order 12345")
   - Broken flow detection ("Find orders delivered but not invoiced")
   - Aggregations, filtering, sorting, and path traversals
3. **Instructions**: Explicit guidance on Cypher syntax, LIMIT clauses, and error handling
4. **User Query**: The actual natural language question

**Retry Logic**:
- Up to 2 retries on LLM failures or invalid Cypher
- Basic syntax validation before execution
- Graceful error messages for translation failures

**Example Prompt Snippet**:
```
SCHEMA:
Nodes: Order(order_id, customer_id, order_date, total_amount, status)
Relationships: (Order)-[:DELIVERED_BY]->(Delivery)

EXAMPLES:
Q: "Show me the top 10 products by number of orders"
A: MATCH (p:Product)<-[:CONTAINS]-(o:Order) 
   RETURN p.name, COUNT(o) AS order_count 
   ORDER BY order_count DESC LIMIT 10

USER QUERY: {natural_language_query}
```

### Guardrail Implementation

The guardrail system uses **keyword-based classification** to validate queries before LLM translation. This design prevents misuse and reduces costs.

**Why Keyword-Based Classification?**
- **Fast**: No LLM call required for validation
- **Deterministic**: Consistent behavior for similar queries
- **Cost-Effective**: Rejects out-of-domain queries before expensive LLM translation
- **Privacy-Preserving**: No external API calls for validation

**Classification Logic**:
- **In-Domain Keywords**: order, delivery, invoice, payment, customer, product, address, billing, shipping, flow, trace, analyze, find, show, list
- **Out-of-Domain Keywords**: weather, sports, news, personal, advice, recipe, movie, music, game, politics

**Decision Process**:
1. Normalize query to lowercase
2. Check for in-domain keyword matches (accept if found)
3. Check for out-of-domain keyword matches (reject if found)
4. For ambiguous cases, default to rejection with helpful message

**Example Rejections**:
- "What's the weather today?" → Rejected (out-of-domain)
- "Tell me a joke" → Rejected (out-of-domain)
- "Show me orders for customer 123" → Accepted (in-domain)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     Chat     │  │    Graph     │  │     Node     │      │
│  │  Interface   │  │  Visualizer  │  │    Detail    │      │
│  │  (Natural    │  │  (React      │  │    Panel     │      │
│  │  Language)   │  │   Flow)      │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                 │                                  │
│         └─────────┬───────┘                                  │
│                   │ HTTP/JSON                                │
└───────────────────┼──────────────────────────────────────────┘
                    │
┌───────────────────┼──────────────────────────────────────────┐
│                   │         Backend Layer                     │
│         ┌─────────▼─────────┐                                │
│         │   FastAPI Server  │                                │
│         │   (REST API)      │                                │
│         └─────────┬─────────┘                                │
│                   │                                           │
│         ┌─────────┼─────────┐                                │
│         │         │         │                                │
│    ┌────▼────┐ ┌──▼──────┐ ┌▼────────────┐                 │
│    │Guardrail│ │  Query  │ │   Neo4j     │                 │
│    │ System  │ │Translator│ │   Service   │                 │
│    │(Keyword)│ │(LLM)    │ │  (Driver)   │                 │
│    └────┬────┘ └──┬──────┘ └┬────────────┘                 │
│         │         │          │                               │
│         │    ┌────▼──────────▼───┐                          │
│         │    │   Data Import     │                          │
│         │    │     Service       │                          │
│         │    └───────────────────┘                          │
└─────────┼──────────┼──────────────┼───────────────────────────┘
          │          │              │
          │     ┌────▼────┐    ┌────▼────────┐
          │     │   LLM   │    │   Neo4j     │
          │     │Provider │    │  Database   │
          │     │(Groq/   │    │  (Graph)    │
          │     │Gemini)  │    └─────────────┘
          │     └─────────┘
          │
          └─ Reject out-of-domain queries
```

**Component Interactions**:
1. User enters natural language query in Chat Interface
2. Frontend sends query to `/api/query` endpoint
3. Guardrail System validates query is in-domain
4. Query Translator sends query + schema to LLM Provider
5. LLM returns Cypher query
6. Neo4j Service executes Cypher against database
7. Results returned to frontend and displayed in Chat Interface
8. Graph Visualizer updates to highlight relevant nodes

## Usage Examples

### Importing Data

Import the sample business data to populate your graph:

```bash
# Import customers
curl -X POST http://localhost:8000/api/import \
  -F "file=@data/customers.csv"

# Import products
curl -X POST http://localhost:8000/api/import \
  -F "file=@data/products.csv"

# Import orders
curl -X POST http://localhost:8000/api/import \
  -F "file=@data/orders.csv"

# Import deliveries, invoices, payments, addresses
curl -X POST http://localhost:8000/api/import \
  -F "file=@data/deliveries.csv"
curl -X POST http://localhost:8000/api/import \
  -F "file=@data/invoices.csv"
curl -X POST http://localhost:8000/api/import \
  -F "file=@data/payments.csv"
curl -X POST http://localhost:8000/api/import \
  -F "file=@data/addresses.csv"
```

### Natural Language Queries

Once data is imported, try these example queries in the chat interface:

**Product Analysis**:
- "Show me the top 10 products by number of orders"
- "Which products have the most invoices?"
- "List products by billing document count"

**Flow Tracing**:
- "Trace the complete flow for order O001"
- "Show me the full process for invoice INV-001"
- "What's the status of order O012?"

**Broken Flow Detection**:
- "Find orders that have been delivered but not invoiced"
- "Show me invoices without payments"
- "Which orders haven't been delivered after 7 days?"

**Customer Analysis**:
- "Show me all orders for customer C001"
- "Which customers have the most orders?"
- "Find customers with unpaid invoices"

**General Queries**:
- "How many orders do we have?"
- "Show me recent deliveries"
- "List all pending payments"

### API Usage Examples

**Submit a query programmatically**:
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the top 5 products by order count",
    "include_cypher": true
  }'
```

**Fetch graph data**:
```bash
curl http://localhost:8000/api/graph?limit=50
```

**Check system health**:
```bash
curl http://localhost:8000/api/health
```

## Development Status

This project is **production-ready** with all core features implemented:

✅ **Data Layer**: Neo4j integration with full CRUD operations  
✅ **Backend API**: FastAPI with all endpoints functional  
✅ **Query Translation**: LLM-powered natural language to Cypher  
✅ **Guardrails**: Domain validation for business intelligence queries  
✅ **Frontend**: React application with graph visualization and chat interface  
✅ **Testing**: Unit tests and integration tests for all components  
✅ **Deployment**: Configuration for Render, Railway, Vercel, and Docker  
✅ **Documentation**: Comprehensive setup and deployment guides  
✅ **SAP O2C Support**: Full support for SAP Order-to-Cash data import and querying

**Sample Data**: 
- The `data/` directory contains example CSV files with 20 orders, 18 deliveries, 15 invoices, 12 payments, 10 customers, 8 products, and 10 addresses, including examples of broken flows for testing.
- The `sap-o2c-data/` directory contains real SAP Order-to-Cash data in JSONL format covering the complete O2C flow: Sales Orders → Deliveries → Billing Documents → Journal Entries → Payments

## SAP Order-to-Cash (O2C) Data

This system includes comprehensive support for SAP O2C data. The `sap-o2c-data/` directory contains:

- **Sales Orders**: Order headers and line items
- **Deliveries**: Outbound delivery documents
- **Billing Documents**: Invoices and billing items
- **Journal Entries**: Accounting documents
- **Payments**: Accounts receivable payments
- **Business Partners**: Customer master data
- **Products**: Material master data
- **Plants**: Warehouse/plant data

### Importing SAP O2C Data

To import the SAP O2C data into your Neo4j database:

```bash
# From project root
python import_sap_data.py
```

The import script will:
1. Connect to your Neo4j database
2. Parse all JSONL files from `sap-o2c-data/`
3. Create nodes for all entities
4. Establish relationships based on the O2C flow
5. Display import statistics

For detailed instructions, see [SAP_O2C_IMPORT_GUIDE.md](SAP_O2C_IMPORT_GUIDE.md)

### Example SAP O2C Queries

Once SAP data is imported, you can ask questions like:

- "Show me the top 10 products by number of sales orders"
- "Trace the complete O2C flow for sales order 740506"
- "Find sales orders that have been delivered but not billed"
- "Which business partners have the most sales orders?"
- "Show me billing documents without payments"
- "What is the total net amount of all billing documents?"
- "Find blocked business partners"
- "Which materials are most frequently ordered?"

## License

MIT

---

## 📚 Additional Documentation

- **[SAP_O2C_IMPORT_GUIDE.md](SAP_O2C_IMPORT_GUIDE.md)** - Detailed SAP data import guide
- **[QUICKSTART_SAP.md](QUICKSTART_SAP.md)** - 5-minute quick start guide
- **[SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)** - Assignment submission checklist
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Complete project summary
- **[SAP_INTEGRATION_SUMMARY.md](SAP_INTEGRATION_SUMMARY.md)** - Technical integration details

## 🎯 Assignment Submission

This project fulfills all requirements for the Forward Deployed Engineer assignment:

✅ **Graph Construction**: Neo4j with SAP O2C entities and relationships  
✅ **Graph Visualization**: Interactive React Flow interface  
✅ **Conversational Interface**: Natural language queries with LLM  
✅ **Example Queries**: Product analysis, flow tracing, broken flow detection  
✅ **Guardrails**: Domain-specific query validation  
✅ **Bonus Features**: Cypher translation, node highlighting, conversation history  

**Demo**: [Your Vercel URL]  
**Repository**: [Your GitHub URL]  
**Submission Form**: https://forms.gle/sPDBUvA45cUM3dyc8

---

**Built with ❤️ using FastAPI, React, Neo4j, and LLM technology**

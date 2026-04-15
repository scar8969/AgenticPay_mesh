# 🎯 AgentPay Mesh - Complete Visual Flow Documentation

## 🚀 **THE COMPLETE QUERY FLOW: FROM INPUT TO RESPONSE**

---

## 📋 **SCENARIO: User submits query "best mechanical keyboard under $100"**

---

## 🔄 **PART 1: OVERALL SYSTEM ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENTPAY MESH SYSTEM                               │
│                                                                              │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│  │   FRONTEND   │         │   BACKEND    │         │  BLOCKCHAIN  │        │
│  │              │         │              │         │              │        │
│  │  Vite+React │◄───────►│  FastAPI     │◄───────►│   Arc Test   │        │
│  │  Port 5173  │  SSE    │  Port 8000   │  API    │    Chain     │        │
│  └──────────────┘         └──────────────┘         └──────────────┘        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    CIRCLE NANOPAYMENTS                                │   │
│  │                   Gas-Free USDC Transfers                            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **PART 2: QUERY PROCESSING FLOW (STEP-BY-STEP)**

### **USER SUBMISSION: "best mechanical keyboard under $100"**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: USER INPUT (FRONTEND)                            │
└─────────────────────────────────────────────────────────────────────────────┘

User types: "best mechanical keyboard under $100"
    ↓
Clicks "Submit" button
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Frontend: Dashboard.tsx                                                   │
│  - Captures query in useState hook                                         │
│  - Sets loading=true, activeAgents=['SearchAgent','ReviewAgent',          │
│    'SummaryAgent']                                                         │
│  - Sends GET request to backend:                                           │
│    GET http://localhost:8000/query?q=best+mechanical+keyboard+under+%24100 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: BACKEND RECEIVES REQUEST                         │
└─────────────────────────────────────────────────────────────────────────────┘

FastAPI Endpoint: /query
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  api/main.py - run_query_get() function                                    │
│                                                                              │
│  @app.get("/query")                                                         │
│  async def run_query_get(q: str):                                           │
│      result = await coordinator.handle_request(q)  # Delegates to           │
│      return result                            #  Coordinator               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: COORDINATOR TAKES OVER                           │
└─────────────────────────────────────────────────────────────────────────────┘

coordinator.py - handle_request() function
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Coordinator thinks: "I need to orchestrate 3 agents and collect payments" │
│                                                                              │
│  def handle_request(self, query: str):                                      │
│      txs = []                                                               │
│      for agent, resource in [                                               │
│          (self.search,  f"/search?q={query}"),    # Agent 1                 │
│          (self.review,  "/review"),                 # Agent 2                 │
│          (self.summary, "/summary"),               # Agent 3                 │
│      ]:                                                                      │
│          # PAYMENT FIRST! Then execute agent                                │
│          tx = await self.payment.pay(...)                                   │
│          txs.append(tx)                                                     │
│                                                                              │
│      # Execute all agents after payments                                    │
│      r1 = await self.search.execute(query)                                  │
│      r2 = await self.review.execute(r1["output"])                           │
│      r3 = await self.summary.execute(r2["output"])                          │
│                                                                              │
│      return {query, final_output, steps, transactions, costs}               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💰 **PART 3: THE PAYMENT FLOW (CRITICAL STEP)**

### **PAYMENT 1: Coordinator → SearchAgent ($0.002)**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           PAYMENT INITIATED: Coordinator pays SearchAgent $0.002            │
└─────────────────────────────────────────────────────────────────────────────┘

payment_service.py - pay() function called
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  PAYMENT RAIL SELECTION LOGIC:                                              │
│                                                                              │
│  Backend thinks: "What payment method should I use?"                         │
│                                                                              │
│  Check prerequisites:                                                        │
│  ├─ USE_NANOPAYMENTS = True ✅                                              │
│  ├─ sender_privkey available = False ❌                                     │
│  ├─ sender_address available = False ❌                                     │
│  └─ receiver_address available = False ❌                                    │
│                                                                              │
│  Decision: MOCK MODE (because credentials missing)                           │
│                                                                              │
│  Rail Selection Reason:                                                      │
│  "Mock mode - prerequisites not met: sender private key missing,            │
│   sender address missing, receiver address missing"                         │
└─────────────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  MOCK PAYMENT EXECUTION:                                                    │
│                                                                              │
│  - Generate mock transaction ID: "a1b2c3d4-..."                             │
│  - Simulate 40ms network delay                                              │
│  - Create transaction record:                                               │
│    {                                                                         │
│      id: "tx_123",                                                          │
│      from: "Coordinator",                                                   │
│      to: "SearchAgent",                                                     │
│      amount: 0.002,                                                         │
│      chain: "mock",                                                        │
│      execution_time_ms: 45.2,                                               │
│      rail_selection_reason: "Mock mode - prerequisites not met",           │
│      api_response: "confirmed"                                              │
│    }                                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRANSACTION BROADCAST:                                                     │
│                                                                              │
│  - Add to in-memory transaction list                                        │
│  - Send via SSE to frontend: "data: {...transaction...}"                    │
│  - Log to console: "[PAY] Coordinator -> SearchAgent: $0.002000 [mock]"    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **PAYMENT 2: Coordinator → ReviewAgent ($0.003)**
```
Same process → Another $0.003 mock payment → Total: $0.005
```

### **PAYMENT 3: Coordinator → SummaryAgent ($0.001)**
```
Same process → Another $0.001 mock payment → Total: $0.006
```

---

## 🤖 **PART 4: AGENT EXECUTION FLOW**

### **AGENT 1: SearchAgent Execution**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           SEARCHAGENT EXECUTION: Search for keyboards                        │
└─────────────────────────────────────────────────────────────────────────────┘

search_agent.py - execute() function
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  SearchAgent thinks: "I need to search for mechanical keyboards under $100" │
│                                                                              │
│  def execute(task_input: str):                                              │
│      # Call DuckDuckGo Instant Answer API                                   │
│      query = task_input                                                      │
│      search_url = f"https://api.duckduckgo.com/?q={query}&format=json"     │
│                                                                              │
│      # Mock response (since no real API in demo mode)                       │
│      results = [                                                             │
│          {"title": "Mechanical Keyboard Guide", "url": "..."},              │
│          {"title": "Best Keyboards 2024", "url": "..."}                     │
│      ]                                                                      │
│                                                                              │
│      return {                                                                │
│          "agent": "SearchAgent",                                            │
│          "input": query,                                                     │
│          "output": f"Found {len(results)} results for: {query}",            │
│          "latency_ms": 564.39                                               │
│      }                                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **AGENT 2: ReviewAgent Execution**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           REVIEWAGENT EXECUTION: Analyze search results                     │
└─────────────────────────────────────────────────────────────────────────────┘

review_agent.py - execute() function
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  ReviewAgent thinks: "I need to analyze these search results and find      │
│                       the best mechanical keyboard"                          │
│                                                                              │
│  def execute(task_input: str):                                              │
│      # Uses Anthropic Claude Haiku for intelligent analysis                 │
│      # (Mock mode returns simulated analysis)                               │
│                                                                              │
│      analysis = f"""                                                         │
│      [Review] Sentiment: positive. Best pick: Product A.                   │
│      Quality: Excellent. Price: $89.                                       │
│      Based on: {task_input}                                                 │
│      """                                                                     │
│                                                                              │
│      return {                                                                │
│          "agent": "ReviewAgent",                                            │
│          "input": task_input,                                                │
│          "output": analysis,                                                 │
│          "latency_ms": 0.0                                                  │
│      }                                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **AGENT 3: SummaryAgent Execution**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           SUMMARYAGENT EXECUTION: Create final recommendation               │
└─────────────────────────────────────────────────────────────────────────────┘

summary_agent.py - execute() function
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  SummaryAgent thinks: "I need to synthesize the review into a clear,      │
│                        concise recommendation"                               │
│                                                                              │
│  def execute(task_input: str):                                              │
│      # Uses Claude Haiku for summary generation                            │
│      # (Mock mode returns simulated summary)                                │
│                                                                              │
│      summary = f"""                                                           │
│      [Summary] Best value: Product A at $349.                              │
│      Recommended for: Mechanical keyboard enthusiasts                       │
│      Based on analysis: {task_input[:50]}...                               │
│      """                                                                     │
│                                                                              │
│      return {                                                                │
│          "agent": "SummaryAgent",                                           │
│          "input": task_input,                                                │
│          "output": summary,                                                  │
│          "latency_ms": 0.0                                                  │
│      }                                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 **PART 5: FRONTEND REAL-TIME UPDATES**

### **SSE (Server-Sent Events) STREAM**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              BACKEND → FRONTEND: REAL-TIME TRANSACTION STREAM              │
└─────────────────────────────────────────────────────────────────────────────┘

Backend sends SSE updates:
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Event 1: Payment 1 completed                                              │
│  data: {                                                                    │
│    "id": "tx_001",                                                         │
│    "from": "Coordinator",                                                  │
│    "to": "SearchAgent",                                                    │
│    "amount": 0.002,                                                        │
│    "chain": "mock",                                                       │
│    "execution_time_ms": 45.2,                                             │
│    "rail_selection_reason": "Mock mode - prerequisites not met",          │
│    "api_response": "confirmed"                                             │
│  }                                                                          │
│                                                                              │
│  Frontend: Dashboard.tsx receives via EventSource                          │
│  eventSource.onmessage = (event) => {                                      │
│      const newTx = JSON.parse(event.data);                                 │
│      setTransactions((prev) => [newTx, ...prev]);  // Live update!         │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Event 2: Payment 2 completed (ReviewAgent)                                │
│  Event 3: Payment 3 completed (SummaryAgent)                               │
│                                                                              │
│  Frontend updates transaction feed in real-time:                            │
│  ┌─────────────────────────────────────────────────────────┐              │
│  │ Live Transaction Feed                                     │              │
│  ├─────────────────────────────────────────────────────────┤              │
│  │ tx_003 | Coordinator → SummaryAgent | $0.001 | mock    │              │
│  │ tx_002 | Coordinator → ReviewAgent   | $0.003 | mock    │              │
│  │ tx_001 | Coordinator → SearchAgent   | $0.002 | mock    │              │
│  └─────────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **PART 6: FINAL RESPONSE TO USER**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKEND ASSEMBLES FINAL RESPONSE                         │
└─────────────────────────────────────────────────────────────────────────────┘

coordinator.py - handle_request() assembles response:
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  {                                                                          │
│    "query": "best mechanical keyboard under $100",                          │
│    "final_output": "[Summary] Best value: Product A at $349.",            │
│    "steps": [                                                               │
│      {                                                                       │
│        "agent": "SearchAgent",                                             │
│        "input": "best mechanical keyboard under $100",                      │
│        "output": "Found 2 results for: best mechanical keyboard...",      │
│        "latency_ms": 564.39                                               │
│      },                                                                      │
│      {                                                                       │
│        "agent": "ReviewAgent",                                             │
│        "input": "Found 2 results for: best mechanical keyboard...",       │
│        "output": "[Review] Sentiment: positive. Best pick: Product A.",  │
│        "latency_ms": 0.0                                                   │
│      },                                                                      │
│      {                                                                       │
│        "agent": "SummaryAgent",                                            │
│        "input": "[Review] Sentiment: positive. Best pick: Product A.",    │
│        "output": "[Summary] Best value: Product A at $349.",              │
│        "latency_ms": 0.0                                                   │
│      }                                                                       │
│    ],                                                                       │
│    "transactions": [/* 3 transactions */],                                  │
│    "total_cost_usdc": 0.006,                                               │
│    "latency_ms": 120.5                                                     │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Frontend receives JSON response:                                           │
│                                                                              │
│  Dashboard.tsx - handleSubmit() function:                                   │
│  - Displays final_output to user                                           │
│  - Updates agent earnings in Agent Status Panel                             │
│  - Shows total cost: $0.006 USDC                                           │
│  - Updates transaction feed with new transactions                           │
│  - Resets loading state, removes active agent highlighting                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 **PART 7: COMPLETE VISUAL DATA FLOW**

```
┌─────────────┐
│   USER      │
│  Types:     │
│  "best      │
│  mechanical │
│  keyboard   │
│  under $100"│
└─────┬───────┘
      │
      │ 1. Submit Query
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Vite+React)                             │
│  http://localhost:5173                                                       │
│                                                                              │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐           │
│  │  Dashboard     │    │  Query Input   │    │  Transaction   │           │
│  │  Component     │    │  Form          │    │  Feed (SSE)    │           │
│  └────────────────┘    └────────────────┘    └────────────────┘           │
│                                                                              │
│  State:                                                                       │
│  - query: "best mechanical keyboard under $100"                             │
│  - loading: true                                                             │
│  - activeAgents: ['SearchAgent','ReviewAgent','SummaryAgent']              │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ 2. GET /query?q=best+mechanical+keyboard+under+%24100
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                 │
│  http://localhost:8000                                                       │
│                                                                              │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐           │
│  │  Coordinator   │───►│ Payment Service│───►│   Circle API   │           │
│  │  Orchestrator  │    │  Rail Selector  │    │  (Nanopayments)│          │
│  └────────────────┘    └────────────────┘    └────────────────┘           │
│                                                                              │
│  Processing:                                                                 │
│  1. Receive query                                                            │
│  2. Plan 3 agent executions                                                 │
│  3. Execute 3 payments                                                      │
│  4. Execute 3 agents                                                        │
│  5. Assemble response                                                        │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ 3a. Pay SearchAgent $0.002
      │ 3b. Pay ReviewAgent $0.003  
      │ 3c. Pay SummaryAgent $0.001
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PAYMENT FLOW (3 Transactions)                           │
│                                                                              │
│  Payment 1: Coordinator → SearchAgent                                       │
│  ├─ Rail Selection: Mock mode (no credentials)                             │
│  ├─ Execution: 45.2ms                                                      │
│  ├─ API Response: confirmed                                                │
│  └─ SSE Broadcast: Immediate frontend update                                │
│                                                                              │
│  Payment 2: Coordinator → ReviewAgent                                       │
│  ├─ Rail Selection: Mock mode                                              │
│  ├─ Execution: 46.5ms                                                      │
│  └─ SSE Broadcast                                                          │
│                                                                              │
│  Payment 3: Coordinator → SummaryAgent                                      │
│  ├─ Rail Selection: Mock mode                                              │
│  ├─ Execution: 47.8ms                                                      │
│  └─ SSE Broadcast                                                          │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ 4. Execute Agents
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AGENT EXECUTION FLOW                                    │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │ SearchAgent │───►│ ReviewAgent │───►│SummaryAgent │                    │
│  │  $0.002/call │    │  $0.003/call│    │ $0.001/call │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│                                                                              │
│  Agent 1: SearchAgent                                                        │
│  ├─ Input: "best mechanical keyboard under $100"                           │
│  ├─ Process: DuckDuckGo API search                                         │
│  ├─ Output: "Found 2 results for: best mechanical keyboard..."           │
│  └─ Latency: 564.39ms                                                      │
│                                                                              │
│  Agent 2: ReviewAgent                                                        │
│  ├─ Input: SearchAgent output                                              │
│  ├─ Process: Claude Haiku analysis                                         │
│  ├─ Output: "[Review] Sentiment: positive. Best pick: Product A."         │
│  └─ Latency: 0.0ms (mock)                                                  │
│                                                                              │
│  Agent 3: SummaryAgent                                                       │
│  ├─ Input: ReviewAgent output                                              │
│  ├─ Process: Claude Haiku summary                                          │
│  ├─ Output: "[Summary] Best value: Product A at $349."                    │
│  └─ Latency: 0.0ms (mock)                                                  │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ 5. Final Response
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESPONSE ASSEMBLY                                     │
│                                                                              │
│  {                                                                          │
│    query: "best mechanical keyboard under $100",                            │
│    final_output: "[Summary] Best value: Product A at $349.",              │
│    steps: [3 agent executions],                                            │
│    transactions: [3 payment records],                                      │
│    total_cost_usdc: 0.006,                                                 │
│    latency_ms: 120.5                                                       │
│  }                                                                          │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ 6. JSON Response + SSE Updates
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND DISPLAY UPDATE                                 │
│                                                                              │
│  User sees:                                                                  │
│  ┌────────────────────────────────────────────────────────┐               │
│  │ Final Answer: [Summary] Best value: Product A at $349. │               │
│  ├────────────────────────────────────────────────────────┤               │
│  │ Cost: $0.006 USDC | Time: 120.5ms                     │               │
│  └────────────────────────────────────────────────────────┘               │
│                                                                              │
│  Live Transaction Feed shows:                                               │
│  ┌────────────────────────────────────────────────────────┐               │
│  │ tx_003 | Coordinator → SummaryAgent | $0.001 | 47.8ms  │               │
│  │ tx_002 | Coordinator → ReviewAgent   | $0.003 | 46.5ms  │               │
│  │ tx_001 | Coordinator → SearchAgent   | $0.002 | 45.2ms  │               │
│  └────────────────────────────────────────────────────────┘               │
│                                                                              │
│  Agent Status Panel updates:                                                 │
│  ┌────────────────────────────────────────────────────────┐               │
│  │ SearchAgent: 1 call | $0.002 earned                    │               │
│  │ ReviewAgent: 1 call  | $0.003 earned                    │               │
│  │ SummaryAgent: 1 call | $0.001 earned                    │               │
│  └────────────────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **PART 8: BATCH DEMO FLOW (25 QUERIES)**

### **WHAT HAPPENS WHEN USER CLICKS "Fire 25-Query Batch"**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BATCH DEMO: 25 QUERIES = 75 TRANSACTIONS                  │
└─────────────────────────────────────────────────────────────────────────────┘

User clicks: "🚀 Fire 25-Query Batch"
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Frontend: Demo.tsx                                                        │
│  - Generates 25 queries: "best laptop under $300", "$320", "$340", ...    │
│  - POST /batch/demo                                                         │
│  - Starts progress tracking                                                 │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ POST /batch/demo
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Backend: coordinator.py - handle_batch()                                  │
│                                                                              │
│  queries = [                                                                │
│    "best laptop under $300",                                                │
│    "best laptop under $320",                                                │
│    "best laptop under $340",                                                │
│    ... (25 total)                                                           │
│  ]                                                                          │
│                                                                              │
│  results = [await self.handle_request(q) for q in queries]                 │
│                                                                              │
│  This creates:                                                              │
│  - 25 queries × 3 agents = 75 agent executions                              │
│  - 75 agent executions × 1 payment each = 75 payments                      │
│  - Total cost: 75 × $0.002 avg = $0.150 USDC                               │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ Processing...
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  BATCH EXECUTION TIMELINE:                                                  │
│                                                                              │
│  Query 1: "best laptop under $300"                                          │
│  ├─ Pay SearchAgent $0.002 → Pay ReviewAgent $0.003 → Pay Summary $0.001  │
│  ├─ Execute SearchAgent → Execute ReviewAgent → Execute SummaryAgent      │
│  └─ Complete: ~600ms, 3 transactions                                       │
│                                                                              │
│  Query 2: "best laptop under $320"                                          │
│  ├─ 3 payments → 3 agent executions                                        │
│  └─ Complete: ~600ms, 3 transactions                                       │
│                                                                              │
│  ... (continues for all 25 queries)                                         │
│                                                                              │
│  Total: 25 queries × 3 payments = 75 transactions                           │
│        Total cost: $0.150 USDC                                              │
│        Total time: ~6 seconds                                               │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ Real-time updates via SSE
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND: REAL-TIME PROGRESS DISPLAY                                       │
│                                                                              │
│  Progress: 0% ████████████████████ 100%                                     │
│  Transactions: 75 / 75                                                      │
│                                                                              │
│  Live Backend Processing:                                                   │
│  ┌────────────────────────────────────────────┐                            │
│  │ tx_075 | Coordinator → SummaryAgent | 47.2ms│                            │
│  │ tx_074 | Coordinator → ReviewAgent   | 46.1ms│                            │
│  │ tx_073 | Coordinator → SearchAgent   | 45.8ms│                            │
│  │ ... showing latest 5 transactions          │                            │
│  └────────────────────────────────────────────┘                            │
│                                                                              │
│  Performance Metrics:                                                        │
│  - Speed: 12.5 tx/s                                                         │
│  - Avg Time: 80ms/tx                                                        │
│  - Elapsed: 6.0s                                                           │
└─────┬──────────────────────────────────────────────────────────────────────┘
      │
      │ Batch Complete
      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUMMARY DISPLAY:                                                            │
│                                                                              │
│  ✅ Batch Complete!                                                          │
│                                                                              │
│  Total Cost:    $0.150000                                                   │
│  Time Elapsed:  6.00s                                                       │
│  Transaction Rate: 12.50 tx/s                                              │
│  Avg Transaction Time: 80ms                                                 │
│                                                                              │
│  Cost Comparison:                                                            │
│  - Nanopayments (Arc): $0.150                                              │
│  - Traditional ($0.50/tx): $37.50                                           │
│  - Savings: 99.6%                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 **PART 9: SYSTEM COMPONENTS INTERACTION**

```
┌─────────────────── COMPLEX SYSTEM INTERACTION ───────────────────┐

│                                                                   │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐│
│  │   FRONTEND  │         │   BACKEND   │         │  EXTERNAL   ││
│  │             │         │             │         │   SERVICES  ││
│  │ Vite+React  │◄───────►│  FastAPI    │◄───────►│             ││
│  │ Port 5173   │  SSE    │  Port 8000   │  HTTP   │             ││
│  └─────────────┘         └─────────────┘         └─────────────┘│
│         │                       │                       │         │
│         │                       │                       │         │
│         │ SSE                   │ API Calls             │         │
│         │ Updates               │ & Payments            │         │
│         │                       │                       │         │
│         ▼                       ▼                       ▼         │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐│
│  │   BROWSER   │         │  PAYMENT    │         │    CIRCLE   ││
│  │             │         │  SERVICE    │         │   NANOPAY   ││
│  │  Dashboard  │         │             │         │             ││
│  │  Demo Page  │         │ Rail Select │         │  Arc Testnet││
│  │  Tx History │         │ Execution   │         │   USDC      ││
│  └─────────────┘         └─────────────┘         └─────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    AGENT ORCHESTRATION                       ││
│  │                                                             ││
│  │  Coordinator pays each agent before execution              ││
│  │                                                             ││
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐                ││
│  │  │  Pay    │───►│  Pay    │───►│  Pay    │                ││
│  │  │Search   │    │Review   │    │Summary  │                ││
│  │  └────┬────┘    └────┬────┘    └────┬────┘                ││
│  │       │              │              │                      ││
│  │       ▼              ▼              ▼                      ││
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐                ││
│  │  │Execute  │    │Execute  │    │Execute  │                ││
│  │  │Search   │───►│Review   │───►│Summary  │                ││
│  │  └─────────┘    └─────────┘    └─────────┘                ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **SUMMARY: COMPLETE QUERY LIFECYCLE**

### **INPUT:** "best mechanical keyboard under $100"

### **PROCESS:**
1. **User submits query** → Frontend captures input
2. **Backend receives request** → Coordinator plans orchestration  
3. **Payment Phase** → 3 payments executed ($0.006 total)
4. **Agent Execution Phase** → 3 agents process sequentially
5. **Response Assembly** → Results combined with transaction records
6. **Real-time Updates** → SSE stream updates frontend live
7. **Final Display** → User sees answer + complete payment history

### **OUTPUT:**
- **Answer:** "[Summary] Best value: Product A at $349."
- **Transactions:** 3 payment records with full backend details
- **Cost:** $0.006 USDC (vs $1.50 traditional on-chain)
- **Time:** 120.5ms total latency

### **BACKEND VISIBILITY:**
- ✅ Rail selection decisions visible
- ✅ Execution timing (45.2ms, 46.5ms, 47.8ms)  
- ✅ API response tracking
- ✅ Payment flow with resource context
- ✅ Real-time processing status

---

**🎯 THIS IS THE COMPLETE FLOW FROM USER QUERY TO FINAL RESPONSE, SHOWING ALL BACKEND THINKING, PAYMENT PROCESSING, AGENT EXECUTION, AND FRONTEND UPDATES IN A PICTORIAL FLOW CHART MANNER!**
<div align="center">

# 💸 AgentPay Mesh

**A multi-agent orchestration system where AI agents autonomously pay each other in USDC via Circle Nanopayments on the Arc blockchain.**

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

A multi-agent orchestration system where AI agents autonomously pay each other in USDC via Circle Nanopayments on Arc blockchain. Each agent execution triggers a micro-payment, demonstrating gas-free, instant value transfer between autonomous AI agents.

## 🏗️ Architecture

AgentPay Mesh consists of three specialized AI agents that collaborate to answer queries:

- **SearchAgent** ($0.002/call): Performs web search using DuckDuckGo Instant Answer API
- **ReviewAgent** ($0.003/call): Analyzes search results using Anthropic Claude Haiku
- **SummaryAgent** ($0.001/call): Synthesizes final recommendations using Claude Haiku

Every agent execution is preceded by a USDC payment through Circle Nanopayments, enabling true agent-to-agent economics.

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.14 + FastAPI | RESTful API with async support |
| **Frontend** | Next.js 14 + TypeScript | Real-time dashboard with SSE |
| **Styling** | Tailwind CSS | Dark theme UI with payment accent colors |
| **Blockchain** | Arc Testnet | Circle's gas-optimized testnet |
| **Payments** | Circle Nanopayments | Gas-free off-chain USDC transfers |
| **Wallets** | Circle Developer Wallets | EOA wallets per agent |
| **AI** | Anthropic Claude Haiku | Fast, cost-effective LLM inference |
| **Search** | DuckDuckGo Instant Answer API | Free web search with no API keys |

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- Node.js 18+
- (Optional) Circle API key for real payments

### 1. Clone and Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your credentials:

```bash
# Required for real payments (optional for demo)
CIRCLE_API_KEY=your_circle_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Agent wallet addresses (set after /setup/wallets)
WALLET_ADDR_COORDINATOR=0x...
WALLET_ADDR_SEARCHAGENT=0x...
WALLET_ADDR_REVIEWAGENT=0x...
WALLET_ADDR_SUMMARYAGENT=0x...
```

### 3. Start Services

**Option A: Concurrent startup (recommended)**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Manual startup**
```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check with stats |
| `/query` | GET/POST | Execute a single query |
| `/batch/demo` | GET | Run 25-query demo batch (75 txs) |
| `/transactions` | GET | Get all transactions |
| `/transactions/live` | GET | SSE stream of live transactions |
| `/agents` | GET | List all agents with stats |
| `/stats` | GET | Comprehensive system statistics |
| `/reset` | DELETE | Reset all data |
| `/setup/wallets` | POST | Create Circle wallets for agents |

## 🎯 Demo Walkthrough

1. **Navigate to Dashboard** (http://localhost:3000)
   - View live metrics and agent status
   - Submit a query: "best mechanical keyboard under $100"
   - Watch 3 payments fire in sequence
   - See transaction feed update in real-time

2. **Run Hackathon Demo** (http://localhost:3000/demo)
   - Click "Fire 25-Query Batch"
   - Watch progress bar fill to 75/75 transactions
   - View summary: $0.150 USDC total cost
   - Compare to traditional: $37.50 (99.6% savings!)

3. **Export Transactions** (http://localhost:3000/transactions)
   - View complete transaction history
   - Click "Export CSV" for judge review
   - Verify chain: "nanopayments/arc"

## 💰 Cost Comparison

| Metric | Nanopayments | Traditional On-Chain |
|--------|-------------|---------------------|
| **Cost per tx** | ~$0.002 | $0.50 |
| **Gas cost** | $0.00 | $2-50 |
| **Confirmation** | Instant | 15s-5min |
| **75 tx batch** | $0.150 | $37.50 |
| **Savings** | - | **99.6%** |

## 🔧 Configuration

### Mock Mode (Default)
Works without any API keys. Uses simulated payments and mock LLM responses.

### Real Mode
Set these environment variables:
```bash
USE_NANOPAYMENTS=true
CIRCLE_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Wallet Setup
```bash
# One-time setup: Create wallets
curl -X POST http://localhost:8000/setup/wallets

# Fund wallets from faucet
# https://faucet.circle.com (select Arc Testnet)
```

## 📁 Project Structure

```
agentpay_mesh/
├── agents/              # AI agent implementations
│   ├── base_agent.py
│   ├── search_agent.py
│   ├── review_agent.py
│   └── summary_agent.py
├── services/            # Payment & blockchain services
│   ├── payment_service.py
│   ├── nanopayments.py
│   ├── circle_wallets.py
│   └── x402_client.py
├── api/                 # FastAPI endpoints
│   └── main.py
├── frontend/            # Next.js dashboard
│   ├── app/
│   │   ├── page.tsx          # Dashboard
│   │   ├── transactions/     # Transaction history
│   │   └── demo/             # Batch demo
│   └── .env.local
├── scripts/             # Utility scripts
│   └── seed_demo.py
├── coordinator.py       # Agent orchestration
├── run.py              # Backend entry point
├── start.sh            # Concurrent startup
└── requirements.txt
```

## 🎨 Frontend Features

- **Real-time Transaction Feed**: SSE-powered live updates
- **Agent Status Panel**: Track earnings and activity per agent
- **Interactive Demo**: Visual batch execution with progress tracking
- **Export Functionality**: CSV export for transaction history
- **Responsive Design**: Mobile-friendly dark theme UI

## 🔐 Security Best Practices

### Critical Security Warnings ⚠️

1. **NEVER commit `.env` files to version control**
   - `.env` is included in `.gitignore` - keep it that way
   - Use `.env.example` as a template only
   - Rotate credentials immediately if accidentally exposed
   - Never share `.env` files via email, chat, or public repositories

2. **Credential Management**
   - Store credentials in environment variables only
   - Use different API keys for dev/staging/production
   - Rotate API keys regularly (recommended: every 90 days)
   - Never log full credentials or partial values that can be reconstructed
   - This project uses secure credential validation that never exposes values

3. **Demo Mode Safety**
   - System works perfectly in mock mode without any credentials
   - Use mock mode for development and testing
   - Only add real credentials when absolutely necessary
   - Mock mode demonstrates all features without security risks

4. **API Key Exposure Indicators**
   - ✅ **SAFE**: Health endpoint shows only `{"configured": true/false, "length": 0}`
   - 🚨 **UNSAFE**: Health endpoint shows `{"preview": "3dc3a230...9fc0"}`
   - If you see credential previews: **IMMEDIATE SECURITY ISSUE**
   - Console output should show lengths only, never partial values

5. **Log File Security**
   - Current configuration: console logging only (no file logs)
   - No sensitive data written to disk
   - If you enable file logging: ensure proper permissions (600)
   - Log rotation recommended for production deployments
   - Never log full API keys, addresses, or partial values

### Security Features Implemented ✅

- **Secure Credential Validation**: Centralized module prevents credential exposure
- **No Partial Credentials**: API responses show only configuration status
- **Safe Console Output**: Length-only display, no partial values
- **Placeholder Detection**: Automatic detection of placeholder vs real credentials
- **Mock Mode Fallback**: System works safely without any credentials
- **Git Protection**: Comprehensive `.gitignore` prevents accidental commits

### Security Checklist 🔍

Before deploying or sharing this project:

- [ ] `.env` file contains only placeholder values (unless actively testing)
- [ ] `.gitignore` exists and prevents credential exposure
- [ ] No API keys visible in `/health` endpoint responses
- [ ] No log files created with sensitive data
- [ ] Console output shows credential lengths only
- [ ] No credentials in git history or backup files
- [ ] Real API keys stored securely (not in code)
- [ ] Team members trained on security practices

### What to Do If Credentials Are Exposed 🚨

1. **Immediate Actions**:
   - Rotate all exposed API keys immediately
   - Change all exposed passwords and secrets
   - Check for unauthorized access/activity
   - Review audit logs for suspicious usage

2. **Code Cleanup**:
   - Remove credentials from all files
   - Use `git filter-branch` to remove from history
   - Force-push cleaned repository
   - Invalidate all exposed tokens

3. **Prevention**:
   - Set up pre-commit hooks to catch credential exposure
   - Use secret scanning tools
   - Implement security code reviews
   - Train team on security best practices

## 🚧 Troubleshooting

**Backend won't start:**
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9
```

**Frontend can't reach backend:**
- Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`
- Check CORS settings in `api/main.py`

**Payments stuck in mock mode:**
- Verify `USE_NANOPAYMENTS=true` in `.env`
- Check Circle API credentials
- Ensure agent wallet addresses are set

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Circle**: Nanopayments & Developer Wallets infrastructure
- **Anthropic**: Claude Haiku for fast, affordable AI inference
- **Arc**: Gas-optimized blockchain for micropayments
- **x402**: HTTP-native payment standard

---

**Built for the AgentPay Hackathon** - Demonstrating the future of AI agent economies on blockchain rails.

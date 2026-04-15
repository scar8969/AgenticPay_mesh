# 🚀 AgentPay Mesh - Complete Startup Guide

## 📋 **PREREQUISITES**

Before starting, ensure you have:

- ✅ **Python 3.14+** installed
- ✅ **Node.js 18+** installed  
- ✅ **Git** (optional, for version control)

---

## 🎯 **QUICK START (5 Minutes)**

### **Option 1: Automatic Startup (Recommended)**

```bash
# Navigate to project directory
cd C:\Users\priya\Desktop\agentpay_mesh

# Start everything with one command
chmod +x start.sh
./start.sh
```

**This will start:**
- Backend on http://localhost:8000
- Frontend on http://localhost:3000 (Next.js)

---

### **Option 2: Manual Startup**

#### **Terminal 1: Start Backend**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh
python run.py
```

#### **Terminal 2: Start Frontend (Choose one)**

**Option A: Next.js Frontend (Original)**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh\frontend
npm run dev
```
Access: http://localhost:3000

**Option B: Vite Frontend (4x Faster - Recommended)**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh\frontend_vite
npm run dev
```
Access: http://localhost:5173

---

## 🔧 **DETAILED SETUP INSTRUCTIONS**

### **STEP 1: Install Dependencies**

#### **Backend Dependencies**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh
pip install -r requirements.txt
```

**Required Python packages:**
- fastapi
- uvicorn
- asyncio
- requests
- python-dotenv

#### **Frontend Dependencies**

**For Next.js Frontend:**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh\frontend
npm install
```

**For Vite Frontend (if not installed):**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh\frontend_vite
npm install
```

---

### **STEP 2: Environment Configuration**

#### **Copy Environment Template**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh
cp .env.example .env
```

#### **Edit .env File (Optional)**
```bash
# For demo mode (default - works without any API keys)
USE_NANOPAYMENTS=false

# For real payments (requires Circle API keys)
# CIRCLE_API_KEY=your_circle_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key
```

**Note**: The system works perfectly in demo/mock mode without any API keys!

---

### **STEP 3: Start the Services**

#### **Backend Service**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh
python run.py
```

**Expected Output:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend URL**: http://localhost:8000

#### **Frontend Service**

**Choose ONE of the following:**

**A. Next.js Frontend (Port 3000)**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh\frontend
npm run dev
```

**B. Vite Frontend (Port 5173 - Recommended)**
```bash
cd C:\Users\priya\Desktop\agentpay_mesh\frontend_vite
npm run dev
```

---

## 🌐 **ACCESS THE APPLICATION**

### **Main Dashboard**
- **Next.js**: http://localhost:3000
- **Vite**: http://localhost:5173 ⚡ **Recommended**

### **Backend API**
- **API Base**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### **Demo Pages**
- **Next.js Demo**: http://localhost:3000/demo
- **Vite Demo**: http://localhost:5173/demo

### **Transaction History**
- **Next.js Transactions**: http://localhost:3000/transactions
- **Vite Transactions**: http://localhost:5173/transactions

---

## 🧪 **TEST THE SETUP**

### **1. Test Backend Health**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-15T...",
  "tx_count": 0,
  "total_paid_usdc": 0.0,
  "system_mode": "mock"
}
```

### **2. Test Single Query**
```bash
curl "http://localhost:8000/query?q=test%20query"
```

### **3. Test Batch Demo**
```bash
curl http://localhost:8000/batch/demo
```

---

## 🎯 **WHAT YOU CAN DO**

### **Dashboard Features**
- ✅ Submit queries and watch real-time agent payments
- ✅ View live transaction feed with backend processing details
- ✅ Monitor agent status and earnings
- ✅ Track system performance metrics

### **Demo Features**
- ✅ Run 25-query batch demo (75 transactions)
- ✅ Watch real-time progress and performance metrics
- ✅ See cost comparison (Nanopayments vs Traditional)
- ✅ Export transaction history as CSV

### **Transaction History**
- ✅ View complete transaction history
- ✅ See backend processing details for each transaction
- ✅ Export data for analysis

---

## 🛠️ **TROUBLESHOOTING**

### **Issue: Port Already in Use**

**Backend (Port 8000):**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
# Or on Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (Port 3000/5173):**
```bash
# Kill process on port 3000
npx kill-port 3000
# Or on Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### **Issue: Dependencies Missing**

**Backend:**
```bash
pip install --upgrade -r requirements.txt
```

**Frontend:**
```bash
cd frontend_vite
npm install
# or
cd frontend
npm install
```

### **Issue: Python Not Found**
```bash
# Check Python version
python --version
# Should show Python 3.14+

# If not found, install Python from:
# https://www.python.org/downloads/
```

### **Issue: Node.js Not Found**
```bash
# Check Node version
node --version
# Should show v18+

# If not found, install Node.js from:
# https://nodejs.org/
```

---

## 📊 **SYSTEM STATUS CHECK**

### **Verify Backend is Running**
```bash
curl http://localhost:8000/health
```

### **Verify Frontend is Running**
Open browser to:
- http://localhost:5173 (Vite)
- http://localhost:3000 (Next.js)

### **Check API Endpoints**
```bash
# List all endpoints
curl http://localhost:8000/docs

# Get system stats
curl http://localhost:8000/stats

# Get agent status
curl http://localhost:8000/agents
```

---

## 🎯 **RECOMMENDED WORKFLOW**

### **For Development:**
```bash
# Terminal 1: Backend
cd C:\Users\priya\Desktop\agentpay_mesh
python run.py

# Terminal 2: Vite Frontend (Faster)
cd C:\Users\priya\Desktop\agentpay_mesh\frontend_vite
npm run dev
```

### **For Testing:**
```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Run test
curl http://localhost:8000/batch/demo
```

### **For Production:**
```bash
# Build Vite frontend
cd frontend_vite
npm run build

# Run backend
cd ..
python run.py
```

---

## 🔑 **KEY COMMANDS**

### **Backend Commands**
```bash
# Start backend
python run.py

# Test health
curl http://localhost:8000/health

# Run demo
curl http://localhost:8000/batch/demo

# Reset data
curl -X DELETE http://localhost:8000/reset
```

### **Frontend Commands**
```bash
# Next.js
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm start           # Start production server

# Vite
cd frontend_vite
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
```

---

## 📝 **ENVIRONMENT VARIABLES**

### **Backend (.env)**
```bash
# Payment Configuration
USE_NANOPAYMENTS=true
CIRCLE_API_KEY=your_circle_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key

# Blockchain Configuration
CIRCLE_BLOCKCHAIN=ARC-TESTNET
ARC_CHAIN_ID=480
USDC_CONTRACT_ARC=0x_USDC_CONTRACT_ON_ARC_TESTNET

# Agent Wallets (set after /setup/wallets)
WALLET_ADDR_COORDINATOR=0x...
WALLET_ADDR_SEARCHAGENT=0x...
WALLET_ADDR_REVIEWAGENT=0x...
WALLET_ADDR_SUMMARYAGENT=0x...
```

### **Frontend (.env.local or .env)**
```bash
# Next.js
NEXT_PUBLIC_API_URL=http://localhost:8000

# Vite
VITE_API_URL=http://localhost:8000
```

---

## 🎯 **SUCCESS INDICATORS**

### **✅ Backend Running Successfully:**
- Terminal shows: `Uvicorn running on http://0.0.0.0:8000`
- Health endpoint returns: `{"status": "healthy"}`
- API docs accessible: http://localhost:8000/docs

### **✅ Frontend Running Successfully:**
- Terminal shows: `Local: http://localhost:5173/` (Vite)
- Browser loads dashboard without errors
- Real-time transaction feed works

### **✅ System Working:**
- Can submit queries
- See live transaction updates
- Agent status cards display correctly
- Demo executes successfully

---

## 🚀 **NEXT STEPS**

1. **Start the services** using the commands above
2. **Open browser** to http://localhost:5173
3. **Submit a query**: "best mechanical keyboard under $100"
4. **Watch the magic**: Real-time payments + agent execution
5. **Run the demo**: Click "Fire 25-Query Batch" button

---

## 📚 **ADDITIONAL RESOURCES**

- **API Documentation**: http://localhost:8000/docs
- **Visual Flow Guide**: See `VISUAL_SYSTEM_DOCUMENTATION.md`
- **Simplified Flow**: See `SIMPLIFIED_VISUAL_FLOW.md`
- **Frontend Enhancement**: See `FRONTEND_BACKEND_VISIBILITY.md`

---

**🎉 That's it! Your AgentPay Mesh system should now be running and ready to demonstrate AI agent-to-agent payments!** 🚀
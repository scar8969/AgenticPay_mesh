# AgentPay Mesh — Setup Guide

## 1. Get Circle API Key
https://console.circle.com → Create account → API Keys

## 2. Install & configure
    cp .env.example .env
    # fill in CIRCLE_API_KEY
    pip install -r requirements.txt

## 3. Create agent wallets on Arc Testnet
    python run.py
    # then POST /setup/wallets
    # copy wallet addresses into .env

## 4. Fund wallets with test USDC
    https://faucet.circle.com
    Select "Arc Testnet" → paste each wallet address

## 5. Start hacking
    GET  /query?q=best+laptop+under+500
    POST /query  {"query": "..."}
    GET  /batch/demo         ← 75 Nanopayment txs on Arc
    GET  /transactions       ← full ledger
    GET  /stats              ← agent + payment analytics

## Tech Stack
    Arc           Settlement layer (EVM L1, USDC gas token)
    USDC          Native value token for all payments
    Nanopayments  Gas-free sub-cent transfers (EIP-3009, off-chain batch)
    Circle Wallets Developer-controlled MPC wallets per agent
    x402          HTTP-native pay-per-request for premium data APIs
    FastAPI        REST backend
    LangGraph     (drop-in upgrade) — wrap each agent.execute() with LLM

## Payment Flow
    Coordinator → sign EIP-3009 → Nanopayments API → instant ledger update
    → SearchAgent executes → Coordinator signs again → ReviewAgent executes
    → Nanopayments batches all txs → settles on Arc periodically (gas-free)

## Economic Proof (for judges)
    Traditional on-chain gas   ~$0.50/tx  ❌
    AgentPay Nanopayments       $0.000    ✓ (Circle covers batch gas)
    Cost per 3-agent request    $0.006 USDC
    Cost for 25-batch demo      $0.150 USDC

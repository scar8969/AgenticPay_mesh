'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Transaction {
  id: string;
  from: string;
  to: string;
  amount: number;
  currency: string;
  timestamp: number;
  status: string;
  chain: string;
  settlement: string;
  gas: string;
  nanopay_ref: string;
}

interface Agent {
  agent: string;
  calls: number;
  total_earned: number;
  wallet: string;
  cost_per_call: number;
  wallet_address: string;
}

interface Stats {
  total_transactions: number;
  total_paid_usdc: number;
  agents: Agent[];
}

export default function Dashboard() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'error'>('checking');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeAgents, setActiveAgents] = useState<string[]>([]);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Poll stats every 3 seconds
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats(data);
          setBackendStatus('healthy');
        } else {
          setBackendStatus('error');
        }
      } catch (error) {
        setBackendStatus('error');
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, [API_URL]);

  // Setup SSE connection for live transactions
  useEffect(() => {
    const eventSource = new EventSource(`${API_URL}/transactions/live`);

    eventSource.onmessage = (event) => {
      const newTx: Transaction = JSON.parse(event.data);
      setTransactions((prev) => [newTx, ...prev].slice(0, 50)); // Keep last 50
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [API_URL]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setActiveAgents(['SearchAgent', 'ReviewAgent', 'SummaryAgent']);

    try {
      const response = await fetch(`${API_URL}/query?q=${encodeURIComponent(query)}`);
      const result = await response.json();

      if (result.transactions) {
        result.transactions.forEach((tx: Transaction) => {
          setTransactions((prev) => [tx, ...prev].slice(0, 50));
        });
      }

      setQuery('');
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
      setActiveAgents([]);
    }
  };

  const formatTimeAgo = (timestamp: number) => {
    const seconds = Math.floor((Date.now() / 1000) - timestamp);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    return `${Math.floor(minutes / 60)}h ago`;
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans">
      {/* Top Bar */}
      <header className="border-b border-gray-800 bg-[#0a0a0a] px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold">AgentPay Mesh</h1>
            <div className={`w-2 h-2 rounded-full ${backendStatus === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          </div>
          <Link href="/demo">
            <button className="bg-[#00ff88] text-black px-4 py-2 rounded-lg font-semibold hover:bg-[#00cc6a] transition-colors">
              New Query
            </button>
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        {/* Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#111111] rounded-lg p-4 border border-gray-800">
            <div className="text-gray-400 text-sm mb-1">Total Transactions</div>
            <div className="text-2xl font-bold font-mono">{stats?.total_transactions || 0}</div>
          </div>
          <div className="bg-[#111111] rounded-lg p-4 border border-gray-800">
            <div className="text-gray-400 text-sm mb-1">Total USDC Paid</div>
            <div className="text-2xl font-bold text-[#00ff88] font-mono">${stats?.total_paid_usdc?.toFixed(6) || '0.000000'}</div>
          </div>
          <div className="bg-[#111111] rounded-lg p-4 border border-gray-800">
            <div className="text-gray-400 text-sm mb-1">Active Agents</div>
            <div className="text-2xl font-bold">3</div>
          </div>
          <div className="bg-[#111111] rounded-lg p-4 border border-gray-800">
            <div className="text-gray-400 text-sm mb-1">Avg Latency</div>
            <div className="text-2xl font-bold font-mono">~120ms</div>
          </div>
        </div>

        {/* Main Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Live Transaction Feed */}
          <div className="lg:col-span-2 bg-[#111111] rounded-lg border border-gray-800">
            <div className="px-4 py-3 border-b border-gray-800">
              <h2 className="font-semibold">Live Transaction Feed</h2>
            </div>
            <div className="divide-y divide-gray-800 max-h-[400px] overflow-y-auto">
              {transactions.length === 0 ? (
                <div className="p-8 text-center text-gray-500">No transactions yet</div>
              ) : (
                transactions.map((tx) => (
                  <div key={tx.id} className="px-4 py-3 hover:bg-[#0d0d0d] transition-colors">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-gray-400">{tx.id.slice(0, 8)}</span>
                        <span className="text-gray-500">→</span>
                        <span className="font-semibold">{tx.from}</span>
                        <span className="text-gray-500">→</span>
                        <span className="font-semibold">{tx.to}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[#00ff88] font-mono font-semibold">${tx.amount.toFixed(6)}</span>
                        <span className={`px-2 py-1 rounded text-xs ${tx.chain.includes('nanopayments') ? 'bg-green-900 text-green-300' : 'bg-gray-700 text-gray-300'}`}>
                          {tx.chain}
                        </span>
                        <span className="text-gray-500 text-xs">{formatTimeAgo(tx.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Agent Status Panel */}
          <div className="bg-[#111111] rounded-lg border border-gray-800">
            <div className="px-4 py-3 border-b border-gray-800">
              <h2 className="font-semibold">Agent Status</h2>
            </div>
            <div className="p-4 space-y-3">
              {stats?.agents.map((agent) => (
                <div key={agent.agent} className="bg-[#0a0a0a] rounded-lg p-3 border border-gray-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">{agent.agent}</span>
                    <div className={`w-2 h-2 rounded-full ${activeAgents.includes(agent.agent) ? 'bg-[#00ff88] animate-pulse' : 'bg-gray-600'}`} />
                  </div>
                  <div className="text-sm text-gray-400 mb-1">
                    Cost: ${agent.cost_per_call ? agent.cost_per_call.toFixed(3) : '0.000'}/call
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Calls: {agent.calls}</span>
                    <span className="text-[#00ff88] font-mono">${agent.total_earned.toFixed(6)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Query Input Bar */}
        <form onSubmit={handleSubmit} className="bg-[#111111] rounded-lg border border-gray-800 p-4 sticky bottom-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 bg-[#0a0a0a] border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#00ff88]"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-[#00ff88] text-black px-6 py-3 rounded-lg font-semibold hover:bg-[#00cc6a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processing...' : 'Submit'}
            </button>
          </div>
        </form>

        {/* Navigation Links */}
        <div className="flex gap-4 mt-6 text-sm text-gray-500">
          <Link href="/transactions" className="hover:text-[#00ff88] transition-colors">
            View All Transactions →
          </Link>
          <Link href="/demo" className="hover:text-[#00ff88] transition-colors">
            Run Demo →
          </Link>
        </div>
      </main>
    </div>
  );
}

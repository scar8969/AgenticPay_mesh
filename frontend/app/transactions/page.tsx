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

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await fetch(`${API_URL}/transactions`);
        const data = await response.json();
        setTransactions(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [API_URL]);

  const exportToCSV = () => {
    const headers = ['TX ID', 'From', 'To', 'Amount', 'Chain', 'Settlement', 'Timestamp'];
    const rows = transactions.map(tx => [
      tx.id,
      tx.from,
      tx.to,
      tx.amount.toFixed(6),
      tx.chain,
      tx.settlement,
      new Date(tx.timestamp * 1000).toISOString()
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  const totalAmount = transactions.reduce((sum, tx) => sum + tx.amount, 0);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center">
        <div className="text-gray-400">Loading transactions...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#0a0a0a] px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <Link href="/">
              <button className="text-gray-400 hover:text-white transition-colors">
                ← Back
              </button>
            </Link>
            <h1 className="text-xl font-bold">Transactions</h1>
          </div>
          <button
            onClick={exportToCSV}
            disabled={transactions.length === 0}
            className="bg-[#00ff88] text-black px-4 py-2 rounded-lg font-semibold hover:bg-[#00cc6a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Export CSV
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        {/* Summary Card */}
        <div className="bg-[#111111] rounded-lg border border-gray-800 p-4 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-gray-400 text-sm">Total Transactions</span>
              <div className="text-2xl font-bold">{transactions.length}</div>
            </div>
            <div className="text-right">
              <span className="text-gray-400 text-sm">Total Amount</span>
              <div className="text-2xl font-bold text-[#00ff88]">${totalAmount.toFixed(6)}</div>
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="bg-[#111111] rounded-lg border border-gray-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#0a0a0a] border-b border-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">TX ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">From</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">To</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Amount</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Chain</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Settlement</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {transactions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                      No transactions yet
                    </td>
                  </tr>
                ) : (
                  transactions.map((tx) => (
                    <tr key={tx.id} className="hover:bg-[#0d0d0d] transition-colors">
                      <td className="px-4 py-3 text-sm font-mono text-gray-400">{tx.id.slice(0, 8)}...</td>
                      <td className="px-4 py-3 text-sm">{tx.from}</td>
                      <td className="px-4 py-3 text-sm">{tx.to}</td>
                      <td className="px-4 py-3 text-sm text-[#00ff88] font-mono font-semibold">${tx.amount.toFixed(6)}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs ${tx.chain.includes('nanopayments') ? 'bg-green-900 text-green-300' : 'bg-gray-700 text-gray-300'}`}>
                          {tx.chain}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-400">{tx.settlement}</td>
                      <td className="px-4 py-3 text-sm text-gray-400">{formatTimestamp(tx.timestamp)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Summary */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Showing {transactions.length} transactions</p>
          <p className="mt-1">Total spent: ${totalAmount.toFixed(6)} USDC</p>
        </div>
      </main>
    </div>
  );
}
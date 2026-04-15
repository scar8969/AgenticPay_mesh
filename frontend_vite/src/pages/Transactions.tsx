import { useEffect, useMemo, useState } from "react";
import AppShell from "../components/AppShell";
import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";
import TonePill from "../components/TonePill";
import {
  formatApiLabel,
  formatChainLabel,
  formatCurrency,
  formatLocalTimestamp,
  formatShortId,
} from "../lib/formatters";
import type { Transaction } from "../lib/types";

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await fetch(`${API_URL}/transactions`);
        if (!response.ok) {
          throw new Error("Failed to fetch transactions");
        }

        const data = (await response.json()) as Transaction[];
        setTransactions(data);
      } catch (fetchError) {
        console.error("Failed to fetch transactions:", fetchError);
        setError("The transaction ledger could not be loaded.");
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [API_URL]);

  const exportToCSV = () => {
    const headers = ["TX ID", "From", "To", "Amount", "Chain", "Settlement", "Timestamp"];
    const rows = transactions.map((tx) => [
      tx.id,
      tx.from,
      tx.to,
      tx.amount.toFixed(6),
      tx.chain,
      tx.settlement,
      new Date(tx.timestamp * 1000).toISOString(),
    ]);

    const csvContent = [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `transactions_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    window.URL.revokeObjectURL(url);
  };

  const totalAmount = useMemo(
    () => transactions.reduce((sum, tx) => sum + tx.amount, 0),
    [transactions]
  );
  const averageExecution = useMemo(() => {
    if (!transactions.length) return 0;
    return (
      transactions.reduce((sum, tx) => sum + tx.execution_time_ms, 0) /
      transactions.length
    );
  }, [transactions]);
  const confirmedCount = useMemo(
    () => transactions.filter((tx) => tx.api_response === "confirmed").length,
    [transactions]
  );

  return (
    <AppShell
      eyebrow="Full ledger"
      title="Transaction history built for demo narration"
      description="A clean, exportable record of every payment hop, optimized for trust-building walkthroughs and investor demos."
      actions={
        <button
          onClick={exportToCSV}
          disabled={!transactions.length}
          className="button-primary"
        >
          Export CSV
        </button>
      }
    >
      <div className="stats-grid">
        <StatCard
          label="Ledger size"
          value={String(transactions.length)}
          detail="Total rows returned from the backend"
        />
        <StatCard
          label="Total amount"
          value={formatCurrency(totalAmount)}
          detail="USDC spent across visible transactions"
          tone="accent"
        />
        <StatCard
          label="Confirmed"
          value={String(confirmedCount)}
          detail="Transactions with confirmed API receipts"
        />
        <StatCard
          label="Average execution"
          value={`${averageExecution.toFixed(1)}ms`}
          detail="Mean time to complete each operation"
          tone="warning"
        />
      </div>

      <SectionCard
        title="Ledger view"
        subtitle="Readable enough for a demo, detailed enough for operators."
      >
        {loading ? (
          <div className="empty-state">Loading transactions...</div>
        ) : error ? (
          <div className="empty-state">{error}</div>
        ) : (
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Transaction</th>
                  <th>Route</th>
                  <th>Amount</th>
                  <th>Rail</th>
                  <th>Execution</th>
                  <th>Selection</th>
                  <th>Response</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {transactions.length ? (
                  transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td>
                        <div className="table-primary">{formatShortId(tx.id)}</div>
                        <div className="table-secondary">{tx.resource || "General request"}</div>
                      </td>
                      <td>
                        <div className="table-primary">
                          {tx.from} → {tx.to}
                        </div>
                        <div className="table-secondary">{tx.currency}</div>
                      </td>
                      <td>
                        <div className="table-primary table-primary--accent">
                          {formatCurrency(tx.amount)}
                        </div>
                      </td>
                      <td>
                        <div className="stack stack--tight">
                          <TonePill tone={formatChainLabel(tx.chain)}>{tx.chain}</TonePill>
                          <span className="table-secondary">{tx.gas}</span>
                        </div>
                      </td>
                      <td>
                        <div className="table-primary">{tx.execution_time_ms.toFixed(1)}ms</div>
                        <div className="table-secondary">{tx.settlement}</div>
                      </td>
                      <td className="table-copy">{tx.rail_selection_reason}</td>
                      <td>
                        <div className="stack stack--tight">
                          <TonePill tone={formatApiLabel(tx.api_response)}>
                            {tx.api_response}
                          </TonePill>
                          {tx.nanopay_ref ? (
                            <span className="table-secondary">
                              {formatShortId(tx.nanopay_ref)}
                            </span>
                          ) : null}
                        </div>
                      </td>
                      <td>
                        <div className="table-primary">
                          {formatLocalTimestamp(tx.timestamp)}
                        </div>
                        <div className="table-secondary">{tx.iso_timestamp}</div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8}>
                      <div className="empty-state">No transactions available yet.</div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </AppShell>
  );
}

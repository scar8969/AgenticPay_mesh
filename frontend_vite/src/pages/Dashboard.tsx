import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AppShell from "../components/AppShell";
import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";
import TonePill from "../components/TonePill";
import {
  formatApiLabel,
  formatChainLabel,
  formatCurrency,
  formatShortId,
  formatTimeAgo,
} from "../lib/formatters";
import type { Stats, Transaction } from "../lib/types";

export default function Dashboard() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [backendStatus, setBackendStatus] = useState<"checking" | "healthy" | "error">(
    "checking"
  );
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeAgents, setActiveAgents] = useState<string[]>([]);
  const [queryError, setQueryError] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/stats`);
        if (!response.ok) {
          throw new Error("Stats fetch failed");
        }

        const data = (await response.json()) as Stats;
        setStats(data);
        setBackendStatus("healthy");
      } catch (error) {
        console.error("Failed to fetch stats:", error);
        setBackendStatus("error");
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, [API_URL]);

  useEffect(() => {
    const eventSource = new EventSource(`${API_URL}/transactions/live`);

    eventSource.onmessage = (event) => {
      const newTx = JSON.parse(event.data) as Transaction;
      setTransactions((prev) => [newTx, ...prev].slice(0, 50));
    };

    eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [API_URL]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setQueryError("");
    setActiveAgents(["SearchAgent", "ReviewAgent", "SummaryAgent"]);

    try {
      const response = await fetch(`${API_URL}/query?q=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error("Query request failed");
      }

      const result = (await response.json()) as { transactions?: Transaction[] };
      if (result.transactions?.length) {
        setTransactions((prev) => [...result.transactions!, ...prev].slice(0, 50));
      }

      setQuery("");
    } catch (error) {
      console.error("Query failed:", error);
      setQueryError("Unable to dispatch the live query right now.");
    } finally {
      setLoading(false);
      setActiveAgents([]);
    }
  };

  const latestTransaction = transactions[0];
  const averageExecution = useMemo(() => {
    if (!transactions.length) return 0;
    return (
      transactions.reduce((sum, tx) => sum + tx.execution_time_ms, 0) /
      transactions.length
    );
  }, [transactions]);
  const nanopaymentCount = useMemo(
    () => transactions.filter((tx) => tx.chain.includes("nanopayments")).length,
    [transactions]
  );

  return (
    <AppShell
      eyebrow="Editorial command center"
      title="Demo-grade visibility into every agent payment"
      description="A sharper view of live mesh activity, backend health, and per-agent spend. Built to read cleanly in a room, on a projector, or in a walkthrough recording."
      actions={
        <div className="hero-actions">
          <div className="status-chip">
            <span className={`status-chip__dot status-chip__dot--${backendStatus}`} />
            Backend {backendStatus}
          </div>
          <Link className="button-primary" to="/demo">
            Run batch demo
          </Link>
        </div>
      }
    >
      <div className="stats-grid">
        <StatCard
          label="Total transactions"
          value={String(stats?.total_transactions ?? 0)}
          detail="Rolling count from the live backend"
        />
        <StatCard
          label="Total spend"
          value={formatCurrency(stats?.total_paid_usdc ?? 0)}
          detail="USDC settled across all agent calls"
          tone="accent"
        />
        <StatCard
          label="Active agents"
          value={String(stats?.agents.length ?? 3)}
          detail="Search, review, and summary workers"
        />
        <StatCard
          label="Average execution"
          value={`${averageExecution.toFixed(1)}ms`}
          detail="Across the current live feed window"
          tone="warning"
        />
      </div>

      <div className="content-grid content-grid--dashboard">
        <div className="stack">
          <SectionCard
            title="Launch a live query"
            subtitle="Trigger a payment flow and watch the ledger populate in real time."
          >
            <form className="query-form" onSubmit={handleSubmit}>
              <textarea
                className="app-input app-input--textarea"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Ask for research, summarization, or review work..."
                disabled={loading}
              />
              <div className="query-form__footer">
                <p className="section-note">
                  AgentPay routes three billable actions per request for the live demo.
                </p>
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="button-primary"
                >
                  {loading ? "Dispatching..." : "Dispatch query"}
                </button>
              </div>
              {queryError ? <p className="error-text">{queryError}</p> : null}
            </form>
          </SectionCard>

          <SectionCard
            title="Backend pulse"
            subtitle="A projector-friendly summary of the most recent transaction."
          >
            {latestTransaction ? (
              <div className="stack">
                <div className="signal-card">
                  <div className="signal-card__header">
                    <p className="signal-card__eyebrow">Latest settlement</p>
                    <TonePill tone={formatChainLabel(latestTransaction.chain)}>
                      {latestTransaction.chain}
                    </TonePill>
                  </div>
                  <div className="signal-card__main">
                    <div>
                      <p className="signal-card__value">
                        {formatCurrency(latestTransaction.amount)}
                      </p>
                      <p className="signal-card__meta">
                        {latestTransaction.from} to {latestTransaction.to}
                      </p>
                    </div>
                    <div className="signal-card__metrics">
                      <span>{latestTransaction.execution_time_ms.toFixed(1)}ms</span>
                      <span>{latestTransaction.settlement}</span>
                      <span>{formatTimeAgo(latestTransaction.timestamp)}</span>
                    </div>
                  </div>
                  <p className="section-note">
                    {latestTransaction.rail_selection_reason}
                  </p>
                </div>

                <div className="detail-grid">
                  <div className="detail-tile">
                    <span className="detail-tile__label">Transaction window</span>
                    <strong>{transactions.length} live items</strong>
                  </div>
                  <div className="detail-tile">
                    <span className="detail-tile__label">Nanopayment mix</span>
                    <strong>{nanopaymentCount} routed via Arc</strong>
                  </div>
                  <div className="detail-tile">
                    <span className="detail-tile__label">Latest reference</span>
                    <strong>{formatShortId(latestTransaction.id, 12)}</strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                No transactions yet. Send a live query to populate this view.
              </div>
            )}
          </SectionCard>

          <SectionCard
            title="Agent earnings"
            subtitle="Who is active, what they cost, and how much each worker has earned."
          >
            <div className="agent-list">
              {(stats?.agents ?? []).map((agent) => (
                <article className="agent-row" key={agent.agent}>
                  <div>
                    <div className="agent-row__title">
                      <h4>{agent.agent}</h4>
                      <span
                        className={`agent-row__status${
                          activeAgents.includes(agent.agent)
                            ? " agent-row__status--active"
                            : ""
                        }`}
                      />
                    </div>
                    <p className="section-note">
                      {formatCurrency(agent.cost_per_call, 3)} per call
                    </p>
                  </div>
                  <div className="agent-row__metrics">
                    <span>{agent.calls} calls</span>
                    <strong>{formatCurrency(agent.total_earned)}</strong>
                  </div>
                </article>
              ))}
            </div>
          </SectionCard>
        </div>

        <SectionCard
          title="Live transaction feed"
          subtitle="Full-fidelity flow details from incoming mesh events."
          action={
            <Link className="button-secondary" to="/transactions">
              Open ledger
            </Link>
          }
        >
          <div className="transaction-stream">
            {transactions.length ? (
              transactions.map((tx) => (
                <article className="transaction-row" key={tx.id}>
                  <div className="transaction-row__topline">
                    <div>
                      <p className="transaction-row__flow">
                        {tx.from} <span>→</span> {tx.to}
                      </p>
                      <p className="transaction-row__id">
                        {formatShortId(tx.id)} · {tx.resource || "general request"}
                      </p>
                    </div>
                    <div className="transaction-row__amount">
                      <strong>{formatCurrency(tx.amount)}</strong>
                      <span>{formatTimeAgo(tx.timestamp)}</span>
                    </div>
                  </div>

                  <div className="transaction-row__meta">
                    <TonePill tone={formatChainLabel(tx.chain)}>{tx.chain}</TonePill>
                    <TonePill tone={formatApiLabel(tx.api_response)}>
                      {tx.api_response}
                    </TonePill>
                    <span>{tx.execution_time_ms.toFixed(1)}ms</span>
                    <span>{tx.gas}</span>
                    <span>{tx.settlement}</span>
                  </div>

                  <p className="transaction-row__reason">{tx.rail_selection_reason}</p>
                </article>
              ))
            ) : (
              <div className="empty-state">
                Waiting for live traffic from the backend event stream.
              </div>
            )}
          </div>
        </SectionCard>
      </div>
    </AppShell>
  );
}

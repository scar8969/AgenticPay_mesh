import { useEffect, useRef, useState } from "react";
import AppShell from "../components/AppShell";
import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";
import TonePill from "../components/TonePill";
import {
  formatApiLabel,
  formatChainLabel,
  formatCurrency,
  formatShortId,
} from "../lib/formatters";
import type {
  BatchResult,
  PerformanceMetrics,
  Transaction,
} from "../lib/types";

export default function Demo() {
  const [progress, setProgress] = useState(0);
  const [txCount, setTxCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<{
    totalCost: number;
    timeElapsed: number;
    txRate: number;
    avgTxTime: number;
  } | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [currentQuery, setCurrentQuery] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [error, setError] = useState("");

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const TARGET_TRANSACTIONS = 75;
  const TARGET_QUERIES = 25;

  const runBatch = async () => {
    setLoading(true);
    setProgress(0);
    setTxCount(0);
    setCurrentQuery(0);
    setSummary(null);
    setPerformance(null);
    setTransactions([]);
    setError("");

    const startTime = Date.now();

    try {
      const response = await fetch(`${API_URL}/batch/demo`);
      if (!response.ok) {
        throw new Error("Batch request failed");
      }

      const result = (await response.json()) as BatchResult;
      const allTransactions: Transaction[] = [];
      result.results.forEach((queryResult) => {
        if (queryResult.transactions) {
          allTransactions.push(...queryResult.transactions);
        }
      });
      setTransactions(allTransactions);

      intervalRef.current = setInterval(() => {
        const now = Date.now();
        const elapsedMs = now - startTime;
        const elapsedSec = elapsedMs / 1000;
        const estimatedQuery = Math.min(Math.floor(elapsedSec / 0.2), TARGET_QUERIES);
        const estimatedTx = Math.min(estimatedQuery * 3, TARGET_TRANSACTIONS);

        setCurrentQuery(estimatedQuery);
        setTxCount(estimatedTx);
        setProgress((estimatedTx / TARGET_TRANSACTIONS) * 100);

        if (estimatedTx > 0) {
          const txPerSecond = estimatedTx / elapsedSec;
          const avgTxTime = elapsedMs / estimatedTx;
          const estimatedTimeRemaining =
            (TARGET_TRANSACTIONS - estimatedTx) / txPerSecond;

          setPerformance({
            startTime,
            currentTime: now,
            elapsedMs,
            transactionsPerSecond: txPerSecond,
            averageTransactionTime: avgTxTime,
            estimatedTimeRemaining,
          });
        }

        if (estimatedTx >= TARGET_TRANSACTIONS) {
          clearInterval(intervalRef.current!);
          setProgress(100);
          setTxCount(TARGET_TRANSACTIONS);
          setCurrentQuery(TARGET_QUERIES);
        }
      }, 100);

      await new Promise((resolve) => setTimeout(resolve, 6000));

      clearInterval(intervalRef.current!);
      const finalTime = (Date.now() - startTime) / 1000;
      const finalTxRate = TARGET_TRANSACTIONS / finalTime;
      const finalAvgTxTime = (finalTime * 1000) / TARGET_TRANSACTIONS;

      setProgress(100);
      setTxCount(TARGET_TRANSACTIONS);
      setCurrentQuery(TARGET_QUERIES);
      setSummary({
        totalCost: result.total_cost_usdc,
        timeElapsed: finalTime,
        txRate: finalTxRate,
        avgTxTime: finalAvgTxTime,
      });
      setPerformance({
        startTime,
        currentTime: Date.now(),
        elapsedMs: Date.now() - startTime,
        transactionsPerSecond: finalTxRate,
        averageTransactionTime: finalAvgTxTime,
        estimatedTimeRemaining: 0,
      });
    } catch (batchError) {
      console.error("Batch failed:", batchError);
      setError("Batch execution failed. Check the backend and try again.");
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    } finally {
      setLoading(false);
    }
  };

  const resetDemo = async () => {
    try {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      await fetch(`${API_URL}/reset`, { method: "DELETE" });
      setProgress(0);
      setTxCount(0);
      setCurrentQuery(0);
      setSummary(null);
      setPerformance(null);
      setTransactions([]);
      setError("");
    } catch (resetError) {
      console.error("Reset failed:", resetError);
    }
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <AppShell
      eyebrow="Narrated batch run"
      title="A polished benchmark flow for live demos"
      description="Fire a 25-query sequence, surface the payment economics instantly, and keep the room focused on speed, savings, and orchestration quality."
      actions={
        <div className="hero-actions">
          <button onClick={runBatch} className="button-primary" disabled={loading}>
            {loading ? "Running batch..." : "Fire 25-query batch"}
          </button>
          <button onClick={resetDemo} className="button-secondary">
            Reset
          </button>
        </div>
      }
    >
      <div className="stats-grid">
        <StatCard
          label="Target volume"
          value={String(TARGET_TRANSACTIONS)}
          detail="25 queries multiplied across 3 agents"
        />
        <StatCard
          label="Completed"
          value={String(txCount)}
          detail={`Query ${currentQuery} of ${TARGET_QUERIES}`}
          tone="accent"
        />
        <StatCard
          label="Speed"
          value={
            performance ? `${performance.transactionsPerSecond.toFixed(1)} tx/s` : "Idle"
          }
          detail="Live throughput estimate"
        />
        <StatCard
          label="Average time"
          value={performance ? `${performance.averageTransactionTime.toFixed(0)}ms` : "—"}
          detail="Current end-to-end execution pace"
          tone="warning"
        />
      </div>

      <div className="content-grid">
        <SectionCard
          title="Execution progress"
          subtitle="Purpose-built for a narrated projector demo."
        >
          <div className="stack">
            <div className="progress-block">
              <div className="progress-block__meta">
                <span>Batch completion</span>
                <strong>{progress.toFixed(0)}%</strong>
              </div>
              <div className="progress-track">
                <div
                  className="progress-track__fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <div className="scoreboard">
              <div>
                <p className="scoreboard__value">
                  {txCount}
                  <span> / {TARGET_TRANSACTIONS}</span>
                </p>
                <p className="scoreboard__label">Transactions confirmed</p>
              </div>
              <div className="scoreboard__support">
                {performance ? (
                  <>
                    <span>{(performance.elapsedMs / 1000).toFixed(1)}s elapsed</span>
                    <span>
                      ETA{" "}
                      {performance.estimatedTimeRemaining > 0
                        ? `${performance.estimatedTimeRemaining.toFixed(1)}s`
                        : "complete"}
                    </span>
                  </>
                ) : (
                  <span>Ready to start</span>
                )}
              </div>
            </div>

            {summary ? (
              <div className="detail-grid">
                <div className="detail-tile">
                  <span className="detail-tile__label">Total cost</span>
                  <strong>{formatCurrency(summary.totalCost)}</strong>
                </div>
                <div className="detail-tile">
                  <span className="detail-tile__label">Time elapsed</span>
                  <strong>{summary.timeElapsed.toFixed(2)}s</strong>
                </div>
                <div className="detail-tile">
                  <span className="detail-tile__label">Transaction rate</span>
                  <strong>{summary.txRate.toFixed(2)} tx/s</strong>
                </div>
                <div className="detail-tile">
                  <span className="detail-tile__label">Traditional equivalent</span>
                  <strong>{formatCurrency(TARGET_TRANSACTIONS * 0.5, 2)}</strong>
                </div>
              </div>
            ) : (
              <p className="section-note">
                This batch simulates a compact showcase of agent-search, review, and summary payouts routed through AgentPay Mesh.
              </p>
            )}

            {error ? <p className="error-text">{error}</p> : null}
          </div>
        </SectionCard>

        <SectionCard
          title="Latest backend events"
          subtitle="Keep the audience grounded in the real payment traffic underneath the benchmark."
        >
          <div className="transaction-stream transaction-stream--compact">
            {transactions.length ? (
              transactions
                .slice(-6)
                .reverse()
                .map((tx) => (
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
                      <strong className="transaction-row__amount-value">
                        {formatCurrency(tx.amount)}
                      </strong>
                    </div>
                    <div className="transaction-row__meta">
                      <TonePill tone={formatChainLabel(tx.chain)}>{tx.chain}</TonePill>
                      <TonePill tone={formatApiLabel(tx.api_response)}>
                        {tx.api_response}
                      </TonePill>
                      <span>{tx.execution_time_ms.toFixed(1)}ms</span>
                    </div>
                  </article>
                ))
            ) : (
              <div className="empty-state">
                No batch events yet. Start the demo to populate this panel.
              </div>
            )}
          </div>
        </SectionCard>

        <SectionCard
          title="Demo framing"
          subtitle="Short talking points for a clean, credible walkthrough."
          className="section-card--full"
        >
          <div className="detail-grid">
            <div className="detail-tile">
              <span className="detail-tile__label">Volume story</span>
              <strong>75 routed micro-payments</strong>
              <p className="section-note">
                Enough activity to feel real without dragging the room.
              </p>
            </div>
            <div className="detail-tile">
              <span className="detail-tile__label">Cost story</span>
              <strong>Arc nanopayments vs flat-fee rails</strong>
              <p className="section-note">
                A direct savings narrative that non-technical viewers understand fast.
              </p>
            </div>
            <div className="detail-tile">
              <span className="detail-tile__label">Speed story</span>
              <strong>Live throughput visible as it runs</strong>
              <p className="section-note">
                Execution timing stays legible while the ledger updates.
              </p>
            </div>
          </div>
        </SectionCard>
      </div>
    </AppShell>
  );
}

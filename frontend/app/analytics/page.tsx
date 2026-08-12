'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  AlertCircle,
  ArrowLeft,
  BarChart3,
  Bot,
  CheckCircle2,
  Clock,
  Globe,
  Phone,
  RefreshCw,
  TrendingDown,
  TrendingUp,
  XCircle,
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface CallRecord {
  id: number;
  session_id: string;
  started_at: string;
  ended_at: string;
  duration: number;
  channel: string;
  outcome: string;
  failure_type: string | null;
  success: number;
  created_at: string;
}

interface Analytics {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  recent_calls: CallRecord[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
  } catch {
    return iso;
  }
}

function successRate(total: number, successful: number): string {
  if (total === 0) return '\u2014';
  return `${Math.round((successful / total) * 100)}%`;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function MetricCard({
  icon,
  label,
  value,
  sublabel,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sublabel?: string;
  color: 'blue' | 'green' | 'red';
}) {
  const ringColor = {
    blue: 'border-blue-500/25 from-blue-600/8 to-indigo-600/8',
    green: 'border-emerald-500/25 from-emerald-600/8 to-teal-600/8',
    red: 'border-rose-500/25 from-rose-600/8 to-red-600/8',
  };
  const iconBg = {
    blue: 'bg-blue-600/10 text-blue-600 dark:text-blue-400',
    green: 'bg-emerald-600/10 text-emerald-600 dark:text-emerald-400',
    red: 'bg-rose-600/10 text-rose-600 dark:text-rose-400',
  };

  return (
    <div
      className={`flex flex-col gap-4 rounded-2xl border bg-gradient-to-br p-6 shadow-sm ${ringColor[color]}`}
    >
      <div className={`flex size-12 items-center justify-center rounded-xl ${iconBg[color]}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm font-semibold text-zinc-500 dark:text-zinc-400">{label}</p>
        <p className="text-foreground mt-1 text-4xl font-extrabold tracking-tight">{value}</p>
        {sublabel && <p className="mt-1 text-xs text-zinc-400">{sublabel}</p>}
      </div>
    </div>
  );
}

function OutcomeBadge({ outcome, failureType }: { outcome: string; failureType: string | null }) {
  const isSuccess = outcome === 'SUCCESS';
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${
        isSuccess
          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400'
          : 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
      }`}
    >
      {isSuccess ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
      {isSuccess ? 'Successful' : failureType ? failureType.replace(/_/g, ' ') : 'Failed'}
    </span>
  );
}

function ChannelBadge({ channel }: { channel: string }) {
  const isSip = channel?.toLowerCase() === 'sip';
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
      {isSip ? <Phone className="size-3" /> : <Globe className="size-3" />}
      {isSip ? 'SIP' : 'Browser'}
    </span>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchAnalytics = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch('/api/analytics', { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      if (!json.success) throw new Error(json.error || 'API error');
      setAnalytics(json.data as Analytics);
      setLastRefresh(new Date());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load analytics. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchAnalytics, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchAnalytics]);

  const total = analytics?.total_calls ?? 0;
  const successful = analytics?.successful_calls ?? 0;
  const failed = analytics?.failed_calls ?? 0;
  const recentCalls = analytics?.recent_calls ?? [];

  return (
    <div className="bg-background text-foreground min-h-screen">
      {/* Background glow */}
      <div className="pointer-events-none fixed -top-40 left-1/2 -z-10 h-[600px] w-[1100px] -translate-x-1/2 rounded-full bg-blue-500/8 blur-[130px]" />

      {/* ── Header ── */}
      <header className="border-border/60 bg-background/80 sticky top-0 z-40 border-b backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="hover:text-foreground flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm font-medium text-zinc-500 transition"
            >
              <ArrowLeft className="size-4" />
              Home
            </Link>
            <span className="text-zinc-300 dark:text-zinc-600">/</span>
            <div className="flex items-center gap-2">
              <div className="flex size-7 items-center justify-center rounded-lg bg-blue-600 text-white">
                <BarChart3 className="size-4" />
              </div>
              <span className="font-semibold">Call Analytics</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {lastRefresh && (
              <span className="hidden text-xs text-zinc-400 sm:block">
                Updated {lastRefresh.toLocaleTimeString('en-IN', { timeStyle: 'medium' })}
              </span>
            )}
            <button
              id="toggle-auto-refresh"
              onClick={() => setAutoRefresh((v) => !v)}
              className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
                autoRefresh
                  ? 'border-emerald-500/40 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400'
                  : 'border-border bg-background text-zinc-500 hover:border-blue-500/40 hover:text-blue-600'
              }`}
            >
              {autoRefresh ? '\u25CF Auto-refresh ON' : 'Auto-refresh'}
            </button>
            <button
              id="manual-refresh"
              onClick={fetchAnalytics}
              disabled={loading}
              className="border-border bg-background flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold text-zinc-500 transition hover:border-blue-500/40 hover:text-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw className={`size-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        {/* Page Title */}
        <div className="mb-10 flex items-center gap-4">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/25">
            <Bot className="size-7" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">FinSahayak AI Analytics</h1>
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
              Real-time call metrics from krishimitra.db &nbsp;&middot;&nbsp; No sensitive caller
              information is displayed
            </p>
          </div>
        </div>

        {/* ── Loading State ── */}
        {loading && !analytics && (
          <div className="flex flex-col items-center gap-4 py-24 text-center text-zinc-400">
            <RefreshCw className="size-8 animate-spin text-blue-500" />
            <p className="text-sm font-medium">Loading analytics&hellip;</p>
          </div>
        )}

        {/* ── Error State ── */}
        {error && (
          <div className="mb-8 flex items-start gap-3 rounded-2xl border border-rose-500/30 bg-rose-50/50 p-5 text-sm dark:bg-rose-950/20">
            <AlertCircle className="mt-0.5 size-5 shrink-0 text-rose-500" />
            <div>
              <p className="font-semibold text-rose-700 dark:text-rose-400">
                Unable to load analytics
              </p>
              <p className="mt-1 text-rose-600/80 dark:text-rose-400/70">{error}</p>
              <button
                onClick={fetchAnalytics}
                className="mt-2 rounded-lg bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-200 dark:bg-rose-900/40 dark:text-rose-300"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {analytics && (
          <>
            {/* ── Three Metric Cards ── */}
            <section aria-label="Call metrics" className="grid grid-cols-1 gap-5 sm:grid-cols-3">
              <MetricCard
                icon={<BarChart3 className="size-6 text-blue-600 dark:text-blue-400" />}
                label="Total Calls"
                value={total}
                sublabel="All recorded sessions"
                color="blue"
              />
              <MetricCard
                icon={<TrendingUp className="size-6 text-emerald-600 dark:text-emerald-400" />}
                label="Successful Calls"
                value={successful}
                sublabel={`${successRate(total, successful)} success rate`}
                color="green"
              />
              <MetricCard
                icon={<TrendingDown className="size-6 text-rose-600 dark:text-rose-400" />}
                label="Failed Calls"
                value={failed}
                sublabel={
                  total > 0 ? `${Math.round((failed / total) * 100)}% of all calls` : '\u2014'
                }
                color="red"
              />
            </section>

            {/* ── Empty State ── */}
            {total === 0 && (
              <div className="mt-12 flex flex-col items-center gap-3 rounded-2xl border border-dashed border-zinc-300 py-16 text-center dark:border-zinc-700">
                <BarChart3 className="size-10 text-zinc-300 dark:text-zinc-600" />
                <p className="text-sm font-semibold text-zinc-500">No calls recorded yet</p>
                <p className="max-w-xs text-xs text-zinc-400">
                  Start a voice session with FinSahayak and complete a financial task to see your
                  first analytics entry.
                </p>
                <Link
                  href="/assistant"
                  className="mt-2 rounded-xl bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  Start a Call
                </Link>
              </div>
            )}

            {/* ── Recent Call History ── */}
            {recentCalls.length > 0 && (
              <section aria-label="Recent calls" className="mt-10">
                <h2 className="mb-1 text-lg font-bold">Recent Call History</h2>
                <p className="mb-5 text-xs text-zinc-400">
                  Showing the last {recentCalls.length} call session
                  {recentCalls.length !== 1 ? 's' : ''}. No personal caller information is stored or
                  displayed.
                </p>

                {/* Desktop table */}
                <div className="border-border/70 hidden overflow-hidden rounded-2xl border md:block">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-border/60 border-b bg-zinc-50/60 dark:bg-zinc-900/60">
                        {['Date / Time', 'Duration', 'Channel', 'Outcome'].map((col) => (
                          <th
                            key={col}
                            className="px-5 py-3 text-left text-xs font-semibold tracking-wider text-zinc-400 uppercase"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {recentCalls.map((call, idx) => (
                        <tr
                          key={call.id}
                          className={`border-border/40 border-b transition-colors hover:bg-zinc-50/50 dark:hover:bg-zinc-900/30 ${
                            idx % 2 !== 0 ? 'bg-zinc-50/30 dark:bg-zinc-900/10' : ''
                          }`}
                        >
                          <td className="px-5 py-3.5">
                            <div className="flex items-center gap-2">
                              <Clock className="size-3.5 text-zinc-400" />
                              <span>{formatDate(call.created_at)}</span>
                            </div>
                          </td>
                          <td className="px-5 py-3.5 font-mono text-xs text-zinc-500">
                            {formatDuration(call.duration)}
                          </td>
                          <td className="px-5 py-3.5">
                            <ChannelBadge channel={call.channel} />
                          </td>
                          <td className="px-5 py-3.5">
                            <OutcomeBadge outcome={call.outcome} failureType={call.failure_type} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Mobile cards */}
                <div className="flex flex-col gap-3 md:hidden">
                  {recentCalls.map((call) => (
                    <div
                      key={call.id}
                      className="border-border/70 bg-card/80 rounded-2xl border p-4"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="text-xs text-zinc-400">{formatDate(call.created_at)}</p>
                          <p className="mt-0.5 font-mono text-xs text-zinc-500">
                            {formatDuration(call.duration)}
                          </p>
                        </div>
                        <OutcomeBadge outcome={call.outcome} failureType={call.failure_type} />
                      </div>
                      <div className="mt-3">
                        <ChannelBadge channel={call.channel} />
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* ── Privacy Notice ── */}
            <div className="mt-10 rounded-2xl border border-zinc-200/60 bg-zinc-50/50 p-5 dark:border-zinc-800 dark:bg-zinc-900/30">
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">
                \uD83D\uDD12 Privacy Notice
              </p>
              <p className="mt-1 text-xs text-zinc-400">
                This dashboard displays only aggregated, non-sensitive call metrics. No caller phone
                numbers, OTPs, PINs, bank account numbers, card details, passwords, or full
                conversation transcripts are stored or shown here.
              </p>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  AlertTriangle,
  Bot,
  CheckCircle,
  CheckCircle2,
  ChevronRight,
  Clock,
  FileText,
  Filter,
  Headset,
  Mail,
  PhoneCall,
  RefreshCw,
  Search,
  ShieldCheck,
  User,
  X,
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';

interface Escalation {
  id: number;
  reference_id: string;
  user_name: string;
  issue_type: string;
  summary: string;
  urgency: string;
  language: string;
  preferred_followup: string;
  status: string;
  agent_checks?: string;
  created_at: string;
  updated_at: string;
}

interface Stats {
  open: number;
  high_priority: number;
  in_progress: number;
  resolved: number;
  total: number;
}

export default function EscalationsPage() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [stats, setStats] = useState<Stats>({
    open: 0,
    high_priority: 0,
    in_progress: 0,
    resolved: 0,
    total: 0,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [urgencyFilter, setUrgencyFilter] = useState('all');
  const [selectedCase, setSelectedCase] = useState<Escalation | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Build query string
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (urgencyFilter !== 'all') params.append('urgency', urgencyFilter);
      if (search) params.append('search', search);

      const [resList, resStats] = await Promise.all([
        fetch(`/api/escalations?${params.toString()}`),
        fetch('/api/escalations/stats'),
      ]);

      const jsonList = await resList.json();
      const jsonStats = await resStats.json();

      if (jsonList.success) {
        setEscalations(jsonList.data || []);
      }
      if (jsonStats.success) {
        setStats(jsonStats.data || {});
      }
    } catch (error) {
      console.error('Error loading escalations:', error);
      toast.error("We couldn't load support requests. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter, urgencyFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchData();
  };

  const handleUpdateStatus = async (newStatus: string) => {
    if (!selectedCase) return;
    setUpdatingStatus(true);
    try {
      const res = await fetch(`/api/escalations/${selectedCase.reference_id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      const json = await res.json();
      if (json.success) {
        toast.success(`Status updated to "${newStatus.replace('_', ' ')}"`);
        setSelectedCase(json.data);
        fetchData();
      } else {
        toast.error(json.error || 'Failed to update status');
      }
    } catch (err) {
      console.error('Error updating status:', err);
      toast.error('Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  return (
    <div className="bg-background text-foreground min-h-screen">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header Bar */}
        <div className="border-border/60 flex flex-col gap-4 border-b pb-6 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-bold text-emerald-600 dark:text-emerald-400">
                <span className="size-2 animate-pulse rounded-full bg-emerald-500" /> System
                Operational
              </span>
              <span className="text-muted-foreground text-xs">| FinSahayak AI</span>
            </div>
            <h1 className="text-foreground mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">
              Human Support Center
            </h1>
            <p className="text-muted-foreground mt-1 text-sm">
              Review and manage financial cases that require human assistance.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              onClick={fetchData}
              variant="outline"
              size="sm"
              className="gap-2 rounded-xl font-medium"
            >
              <RefreshCw className={`size-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
            </Button>
            <Button
              asChild
              size="sm"
              className="rounded-xl bg-blue-600 font-semibold text-white hover:bg-blue-700"
            >
              <Link href="/assistant">
                <Bot className="mr-2 size-4" /> Open Assistant
              </Link>
            </Button>
          </div>
        </div>

        {/* Statistics Cards Grid */}
        <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {/* Card 1: Open Requests */}
          <div className="border-border/70 bg-card rounded-2xl border p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground text-xs font-bold uppercase">
                Open Requests
              </span>
              <div className="flex size-9 items-center justify-center rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400">
                <Clock className="size-5" />
              </div>
            </div>
            <p className="text-foreground mt-3 text-3xl font-extrabold">{stats.open}</p>
            <p className="text-muted-foreground mt-1 text-xs">Awaiting initial review</p>
          </div>

          {/* Card 2: High Priority */}
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/5 p-5 shadow-sm dark:bg-rose-950/20">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-rose-600 uppercase dark:text-rose-400">
                High Priority
              </span>
              <div className="flex size-9 items-center justify-center rounded-xl bg-rose-500/20 text-rose-600 dark:text-rose-400">
                <AlertTriangle className="size-5" />
              </div>
            </div>
            <p className="mt-3 text-3xl font-extrabold text-rose-600 dark:text-rose-400">
              {stats.high_priority}
            </p>
            <p className="mt-1 text-xs text-rose-600/80 dark:text-rose-400/80">
              Requires immediate attention
            </p>
          </div>

          {/* Card 3: In Progress */}
          <div className="border-border/70 bg-card rounded-2xl border p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground text-xs font-bold uppercase">In Progress</span>
              <div className="flex size-9 items-center justify-center rounded-xl bg-blue-500/15 text-blue-600 dark:text-blue-400">
                <Headset className="size-5" />
              </div>
            </div>
            <p className="text-foreground mt-3 text-3xl font-extrabold">{stats.in_progress}</p>
            <p className="text-muted-foreground mt-1 text-xs">Currently being resolved</p>
          </div>

          {/* Card 4: Resolved */}
          <div className="border-border/70 bg-card rounded-2xl border p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground text-xs font-bold uppercase">Resolved</span>
              <div className="flex size-9 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400">
                <CheckCircle className="size-5" />
              </div>
            </div>
            <p className="text-foreground mt-3 text-3xl font-extrabold">{stats.resolved}</p>
            <p className="text-muted-foreground mt-1 text-xs">Successfully closed cases</p>
          </div>
        </div>

        {/* Filters & Search Toolbar */}
        <div className="border-border/70 bg-card mt-8 flex flex-col gap-4 rounded-2xl border p-4 shadow-sm md:flex-row md:items-center md:justify-between">
          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 md:w-80">
            <div className="relative w-full">
              <Search className="text-muted-foreground absolute top-1/2 left-3 size-4 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search reference ID, user..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="border-border/80 bg-background text-foreground w-full rounded-xl border py-2 pr-4 pl-9 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <Button type="submit" size="sm" variant="secondary" className="rounded-xl">
              Search
            </Button>
          </form>

          <div className="flex flex-wrap items-center gap-3">
            {/* Status Filter */}
            <div className="text-muted-foreground flex items-center gap-1.5 text-xs font-semibold">
              <Filter className="size-3.5" />
              <span>Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border-border/80 bg-background text-foreground rounded-xl border px-3 py-1.5 text-xs font-medium focus:outline-none"
              >
                <option value="all">All Statuses</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>

            {/* Urgency Filter */}
            <div className="text-muted-foreground flex items-center gap-1.5 text-xs font-semibold">
              <span>Urgency:</span>
              <select
                value={urgencyFilter}
                onChange={(e) => setUrgencyFilter(e.target.value)}
                className="border-border/80 bg-background text-foreground rounded-xl border px-3 py-1.5 text-xs font-medium focus:outline-none"
              >
                <option value="all">All Urgencies</option>
                <option value="high">High / Emergency</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
        </div>

        {/* Requests Table & Responsive Content */}
        <div className="border-border/70 bg-card mt-6 overflow-hidden rounded-2xl border shadow-sm">
          {loading ? (
            <div className="text-muted-foreground py-16 text-center text-sm">
              <RefreshCw className="mx-auto mb-2 size-6 animate-spin text-blue-600" />
              Loading support requests...
            </div>
          ) : escalations.length === 0 ? (
            <div className="py-16 text-center">
              <Headset className="text-muted-foreground/60 mx-auto mb-3 size-10" />
              <h3 className="text-foreground text-lg font-bold">No human support requests yet</h3>
              <p className="text-muted-foreground mx-auto mt-1 max-w-sm text-sm">
                FinSahayak will show requests here when callers give permission for human
                assistance.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-border/70 bg-muted/40 text-muted-foreground border-b text-xs font-semibold uppercase">
                  <tr>
                    <th className="px-6 py-4">Reference ID</th>
                    <th className="px-6 py-4">User</th>
                    <th className="px-6 py-4">Issue</th>
                    <th className="px-6 py-4">Urgency</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Language</th>
                    <th className="px-6 py-4">Follow-up</th>
                    <th className="px-6 py-4">Created</th>
                    <th className="px-6 py-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-border/60 divide-y">
                  {escalations.map((item) => (
                    <tr
                      key={item.id}
                      onClick={() => setSelectedCase(item)}
                      className="hover:bg-muted/50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 font-mono font-bold text-blue-600 dark:text-blue-400">
                        {item.reference_id}
                      </td>
                      <td className="text-foreground px-6 py-4 font-medium">{item.user_name}</td>
                      <td className="text-muted-foreground px-6 py-4">{item.issue_type}</td>
                      <td className="px-6 py-4">
                        {item.urgency === 'high' || item.urgency === 'emergency' ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/15 px-2.5 py-0.5 text-xs font-bold text-rose-600 dark:text-rose-400">
                            HIGH
                          </span>
                        ) : item.urgency === 'medium' ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2.5 py-0.5 text-xs font-bold text-amber-600 dark:text-amber-400">
                            MEDIUM
                          </span>
                        ) : (
                          <span className="text-muted-foreground inline-flex items-center gap-1 rounded-full bg-slate-500/15 px-2.5 py-0.5 text-xs font-bold">
                            LOW
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {item.status === 'open' ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2.5 py-0.5 text-xs font-bold text-amber-600 dark:text-amber-400">
                            OPEN
                          </span>
                        ) : item.status === 'in_progress' ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-blue-500/15 px-2.5 py-0.5 text-xs font-bold text-blue-600 dark:text-blue-400">
                            IN PROGRESS
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-xs font-bold text-emerald-600 dark:text-emerald-400">
                            RESOLVED
                          </span>
                        )}
                      </td>
                      <td className="text-muted-foreground px-6 py-4">{item.language}</td>
                      <td className="text-muted-foreground px-6 py-4">{item.preferred_followup}</td>
                      <td className="text-muted-foreground px-6 py-4 text-xs">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Button variant="ghost" size="sm" className="rounded-lg text-xs">
                          View <ChevronRight className="ml-1 size-3.5" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Case Detail Modal Drawer */}
      {selectedCase && (
        <div className="bg-background/80 fixed inset-0 z-50 flex items-center justify-end p-4 backdrop-blur-sm">
          <div className="border-border/80 bg-card h-full w-full max-w-lg overflow-y-auto rounded-3xl border p-6 shadow-2xl">
            {/* Drawer Header */}
            <div className="border-border/60 flex items-center justify-between border-b pb-4">
              <div>
                <span className="font-mono text-xs font-bold text-blue-600 dark:text-blue-400">
                  {selectedCase.reference_id}
                </span>
                <h2 className="text-foreground text-xl font-bold">{selectedCase.issue_type}</h2>
              </div>
              <button
                onClick={() => setSelectedCase(null)}
                className="text-muted-foreground hover:bg-muted rounded-full p-1.5"
              >
                <X className="size-5" />
              </button>
            </div>

            {/* Status Selector */}
            <div className="bg-muted/40 mt-5 rounded-2xl p-4">
              <label className="text-muted-foreground mb-2 block text-xs font-bold tracking-wider uppercase">
                Update Case Status
              </label>
              <div className="flex items-center gap-2">
                <select
                  value={selectedCase.status}
                  onChange={(e) => handleUpdateStatus(e.target.value)}
                  disabled={updatingStatus}
                  className="border-border/80 bg-background text-foreground w-full rounded-xl border px-3 py-2 text-sm font-semibold focus:outline-none"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
            </div>

            {/* Case Information Metadata */}
            <div className="mt-6 space-y-4 text-xs">
              <div className="border-border/60 bg-card grid grid-cols-2 gap-3 rounded-2xl border p-4">
                <div>
                  <span className="text-muted-foreground block">Customer Name</span>
                  <span className="text-foreground text-sm font-bold">
                    {selectedCase.user_name}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Urgency Level</span>
                  <span className="text-foreground text-sm font-bold uppercase">
                    {selectedCase.urgency}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Language</span>
                  <span className="text-foreground text-sm font-bold">{selectedCase.language}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Preferred Follow-up</span>
                  <span className="text-foreground text-sm font-bold">
                    {selectedCase.preferred_followup}
                  </span>
                </div>
              </div>

              {/* Human Summary */}
              <div className="border-border/60 bg-card rounded-2xl border p-4">
                <span className="text-foreground mb-1 block text-sm font-bold">Human Summary</span>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {selectedCase.summary}
                </p>
              </div>

              {/* Agent Checks */}
              <div className="rounded-2xl border border-blue-500/30 bg-blue-500/5 p-4">
                <span className="mb-1 block text-sm font-bold text-blue-600 dark:text-blue-400">
                  Agent Checks
                </span>
                <p className="text-muted-foreground text-xs leading-relaxed">
                  {selectedCase.agent_checks ||
                    'FinSahayak identified the report and verified user permission before creating human support request.'}
                </p>
              </div>

              {/* Recommended Next Action */}
              <div className="rounded-2xl border border-amber-500/30 bg-amber-500/5 p-4">
                <span className="mb-1 block text-sm font-bold text-amber-600 dark:text-amber-400">
                  Next Action
                </span>
                <p className="text-muted-foreground text-xs leading-relaxed">
                  Human support representative should review the reported case details and contact
                  the user through the selected follow-up method ({selectedCase.preferred_followup}
                  ).
                </p>
              </div>
            </div>

            {/* Footer Close */}
            <div className="border-border/60 mt-8 border-t pt-4 text-right">
              <Button onClick={() => setSelectedCase(null)} className="rounded-xl">
                Close Panel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

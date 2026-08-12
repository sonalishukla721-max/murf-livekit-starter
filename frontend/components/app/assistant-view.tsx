'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Bot,
  ChevronLeft,
  Headset,
  HelpCircle,
  History,
  MessageSquare,
  Mic,
  PhoneCall,
  Plus,
  Settings,
  ShieldCheck,
  Sparkles,
  User,
} from 'lucide-react';
import { AppConfig } from '@/app-config';
import { App } from '@/components/app/app';
import { Button } from '@/components/ui/button';

interface AssistantViewProps {
  appConfig: AppConfig;
}

export function AssistantView({ appConfig }: AssistantViewProps) {
  const searchParams = useSearchParams();
  const initialPrompt = searchParams.get('prompt');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedPrompt, setSelectedPrompt] = useState<string | null>(initialPrompt);

  const starterPrompts = [
    'What is a savings account?',
    'How does EMI work?',
    'Help me understand a loan',
    'Show me financial schemes',
    'I need human support',
  ];

  return (
    <div className="bg-background flex h-[calc(100vh-4rem)] w-full overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-16'
        } border-border/60 bg-card/60 flex shrink-0 flex-col border-r transition-all duration-300`}
      >
        {/* Sidebar Header */}
        <div className="border-border/50 flex h-14 items-center justify-between border-b px-4">
          {sidebarOpen ? (
            <div className="flex items-center gap-2">
              <div className="flex size-7 items-center justify-center rounded-lg bg-blue-600 text-white">
                <Bot className="size-4" />
              </div>
              <span className="text-foreground text-sm font-bold">Assistant Hub</span>
            </div>
          ) : (
            <div className="mx-auto flex size-7 items-center justify-center rounded-lg bg-blue-600 text-white">
              <Bot className="size-4" />
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-muted-foreground hover:bg-muted hover:text-foreground rounded-lg p-1"
            title="Toggle Sidebar"
          >
            <ChevronLeft
              className={`size-4 transition-transform ${!sidebarOpen ? 'rotate-180' : ''}`}
            />
          </button>
        </div>

        {/* Sidebar Actions */}
        <div className="flex flex-1 flex-col gap-1 p-2">
          <Button
            variant="default"
            size="sm"
            className="w-full justify-start gap-2.5 rounded-xl bg-blue-600 font-medium text-white hover:bg-blue-700"
          >
            <Plus className="size-4 shrink-0" />
            {sidebarOpen && <span>New Conversation</span>}
          </Button>

          <div className="border-border/50 my-2 border-t" />

          {sidebarOpen && (
            <span className="text-muted-foreground px-2 text-[10px] font-bold tracking-wider uppercase">
              Navigation
            </span>
          )}

          <button className="flex items-center gap-2.5 rounded-xl bg-blue-50 px-3 py-2 text-sm font-medium text-blue-600 dark:bg-blue-950/40 dark:text-blue-400">
            <Bot className="size-4 shrink-0 text-blue-600 dark:text-blue-400" />
            {sidebarOpen && <span>FinSahayak Agent</span>}
          </button>

          <Link
            href="/escalations"
            className="text-muted-foreground hover:bg-muted hover:text-foreground flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm font-medium"
          >
            <Headset className="size-4 shrink-0 text-amber-500" />
            {sidebarOpen && (
              <div className="flex w-full items-center justify-between">
                <span>Human Support</span>
                <span className="rounded-full bg-amber-500/20 px-1.5 py-0.5 text-[10px] font-bold text-amber-600 dark:text-amber-400">
                  Day 7
                </span>
              </div>
            )}
          </Link>

          <button className="text-muted-foreground hover:bg-muted hover:text-foreground flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm font-medium">
            <History className="size-4 shrink-0" />
            {sidebarOpen && <span>Recent Sessions</span>}
          </button>

          <button className="text-muted-foreground hover:bg-muted hover:text-foreground flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm font-medium">
            <User className="size-4 shrink-0" />
            {sidebarOpen && <span>User Memory</span>}
          </button>
        </div>

        {/* Sidebar Footer */}
        <div className="border-border/50 border-t p-3">
          <div className="bg-muted/40 flex items-center gap-2 rounded-xl p-2">
            <ShieldCheck className="size-4 shrink-0 text-emerald-500" />
            {sidebarOpen && (
              <div className="flex flex-col">
                <span className="text-foreground text-xs font-semibold">
                  Safe & Privacy Guarded
                </span>
                <span className="text-muted-foreground text-[10px]">No passwords/OTPs needed</span>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Agent Content Area */}
      <main className="bg-background relative flex flex-1 flex-col overflow-hidden">
        {/* Header Bar */}
        <header className="border-border/60 bg-card/40 flex h-14 items-center justify-between border-b px-6">
          <div className="flex items-center gap-3">
            <div className="flex size-8 items-center justify-center rounded-lg bg-blue-600 text-white">
              <Bot className="size-4" />
            </div>
            <div>
              <h2 className="text-foreground text-sm font-bold">FinSahayak AI</h2>
              <p className="flex items-center gap-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                <span className="size-1.5 animate-pulse rounded-full bg-emerald-500" /> Online •
                Financial Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link href="/escalations">
              <Button
                variant="outline"
                size="sm"
                className="h-8 gap-1.5 rounded-xl border-amber-500/40 text-xs font-semibold text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-950/40"
              >
                <Headset className="size-3.5" /> Need Human Support?
              </Button>
            </Link>
          </div>
        </header>

        {/* LiveKit Voice/Chat Container */}
        <div className="relative flex-1 overflow-hidden">
          <App appConfig={appConfig} />
        </div>
      </main>
    </div>
  );
}

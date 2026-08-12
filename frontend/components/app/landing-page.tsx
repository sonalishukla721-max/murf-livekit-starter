'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  FileCheck,
  Headset,
  HelpCircle,
  Lock,
  MessageSquare,
  Mic,
  PhoneCall,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export function LandingPage() {
  const router = useRouter();
  const [selectedPrompt, setSelectedPrompt] = useState<string | null>(null);

  const heroPrompts = [
    'What is a savings account?',
    'How does EMI work?',
    'Show me available financial schemes',
    'I need human support',
  ];

  const handlePromptClick = (prompt: string) => {
    setSelectedPrompt(prompt);
    router.push(`/assistant?prompt=${encodeURIComponent(prompt)}`);
  };

  return (
    <div className="bg-background text-foreground relative min-h-screen overflow-hidden">
      {/* Subtle Background Lighting Gradients */}
      <div className="pointer-events-none absolute -top-40 left-1/2 -z-10 h-[500px] w-[1000px] -translate-x-1/2 rounded-full bg-blue-500/10 blur-[120px] dark:bg-blue-600/15" />
      <div className="pointer-events-none absolute top-[600px] right-0 -z-10 h-[400px] w-[400px] rounded-full bg-indigo-500/10 blur-[100px]" />

      {/* ======================================================== */}
      {/* HERO SECTION                                             */}
      {/* ======================================================== */}
      <section className="mx-auto max-w-7xl px-4 pt-12 pb-20 sm:px-6 md:pt-20 md:pb-28 lg:px-8">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-12 lg:gap-8">
          {/* Left Column — Copy & CTAs */}
          <div className="flex flex-col items-start lg:col-span-7">
            {/* Small Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50/80 px-3.5 py-1.5 text-xs font-semibold text-blue-700 backdrop-blur-sm dark:border-blue-900/60 dark:bg-blue-950/40 dark:text-blue-300">
              <Sparkles className="size-3.5 text-blue-600 dark:text-blue-400" />
              <span>AI-POWERED FINANCIAL ASSISTANCE</span>
            </div>

            {/* Main Heading */}
            <h1 className="text-foreground mt-6 text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl md:leading-[1.15]">
              Your Smarter Way to <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 bg-clip-text text-transparent dark:from-blue-400 dark:via-indigo-400 dark:to-blue-300">
                Navigate Finance.
              </span>
            </h1>

            {/* Supporting Text */}
            <p className="text-muted-foreground mt-6 text-lg leading-relaxed font-normal sm:text-xl">
              FinSahayak AI helps you understand financial services, get personalized guidance, and
              connect with human support when your situation needs expert attention.
            </p>

            {/* Primary & Secondary CTAs */}
            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
              <Button
                asChild
                size="lg"
                className="h-13 rounded-2xl bg-blue-600 px-8 text-base font-semibold text-white shadow-lg shadow-blue-600/25 transition-all hover:bg-blue-700 hover:shadow-blue-600/35 active:scale-[0.98]"
              >
                <Link href="/assistant">
                  <Mic className="mr-2 size-5" /> Talk to FinSahayak
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="border-border hover:bg-muted h-13 rounded-2xl px-7 text-base font-semibold transition-all"
              >
                <a href="#features">Explore Features</a>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="border-border hover:bg-muted h-13 rounded-2xl px-7 text-base font-semibold transition-all"
              >
                <Link href="/analytics">
                  <BarChart3 className="mr-2 size-4" /> Analytics
                </Link>
              </Button>
            </div>

            {/* Quick Metrics */}
            <div className="border-border/60 text-muted-foreground mt-10 flex items-center gap-6 border-t pt-6 text-xs sm:gap-8">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="size-4 text-emerald-500" />
                <span>Powered by Murf Falcon TTS</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="size-4 text-blue-500" />
                <span>Zero Credentials Stored</span>
              </div>
              <div className="flex items-center gap-2">
                <Headset className="size-4 text-indigo-500" />
                <span>Day 7 Human Escalation</span>
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 className="size-4 text-violet-500" />
                <Link href="/analytics" className="hover:text-foreground underline-offset-2 hover:underline">Day 8 Analytics</Link>
              </div>
            </div>
          </div>

          {/* Right Column — Interactive Assistant Preview Card */}
          <div className="lg:col-span-5">
            <div className="border-border/80 bg-card/90 relative mx-auto max-w-md rounded-3xl border p-6 shadow-2xl backdrop-blur-xl transition-all hover:border-blue-500/30 dark:shadow-blue-950/20">
              {/* Card Header */}
              <div className="border-border/60 flex items-center justify-between border-b pb-4">
                <div className="flex items-center gap-3">
                  <div className="relative flex size-10 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
                    <Bot className="size-6" />
                    <span className="ring-card absolute -top-1 -right-1 size-3 rounded-full bg-emerald-500 ring-2" />
                  </div>
                  <div>
                    <h3 className="text-foreground font-bold">FinSahayak AI</h3>
                    <p className="text-xs font-medium text-emerald-600 dark:text-emerald-400">
                      ● Ready to Assist
                    </p>
                  </div>
                </div>
                <span className="rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
                  Voice & Chat
                </span>
              </div>

              {/* Chat Preview Body */}
              <div className="my-5 flex flex-col gap-3">
                <div className="bg-muted/80 text-foreground self-start rounded-2xl rounded-tl-sm px-4 py-3 text-sm">
                  <p className="font-medium">Hi! How can I help you today?</p>
                  <p className="text-muted-foreground mt-1 text-xs">
                    Ask me any financial question or try a suggested topic below:
                  </p>
                </div>

                {/* Suggested Prompts List */}
                <div className="mt-2 flex flex-col gap-2">
                  <p className="text-muted-foreground text-[11px] font-semibold tracking-wider uppercase">
                    Suggested Questions:
                  </p>
                  {heroPrompts.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handlePromptClick(prompt)}
                      className="border-border/70 bg-background/60 text-foreground flex items-center justify-between rounded-xl border px-3.5 py-2.5 text-left text-xs font-medium transition-all hover:border-blue-500/40 hover:bg-blue-50/50 hover:text-blue-600 dark:hover:bg-blue-950/30 dark:hover:text-blue-300"
                    >
                      <span>"{prompt}"</span>
                      <ArrowRight className="text-muted-foreground size-3.5" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Central Voice Action Controls */}
              <div className="border-border/60 border-t pt-4 text-center">
                <Button
                  asChild
                  className="w-full rounded-2xl bg-blue-600 py-6 text-sm font-semibold text-white shadow-md hover:bg-blue-700"
                >
                  <Link href="/assistant">
                    <Mic className="mr-2 size-4 animate-pulse" /> Start Voice Session
                  </Link>
                </Button>
                <p className="text-muted-foreground mt-2.5 text-[11px]">
                  Click to launch interactive LiveKit + Murf voice assistant
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ======================================================== */}
      {/* TRUST / VALUE SECTION                                    */}
      {/* ======================================================== */}
      <section className="border-border/60 bg-muted/30 border-y py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-muted-foreground text-center text-xs font-bold tracking-widest uppercase">
            Built to make financial assistance simpler, safer, and more accessible.
          </p>
          <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="border-border/60 bg-card/60 flex items-center gap-3.5 rounded-2xl border p-4 shadow-sm">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
                <Zap className="size-5" />
              </div>
              <div>
                <h4 className="text-foreground text-sm font-bold">AI-Powered Assistance</h4>
                <p className="text-muted-foreground text-xs">Instant voice & chat responses</p>
              </div>
            </div>

            <div className="border-border/60 bg-card/60 flex items-center gap-3.5 rounded-2xl border p-4 shadow-sm">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                <TrendingUp className="size-5" />
              </div>
              <div>
                <h4 className="text-foreground text-sm font-bold">Real Financial Data</h4>
                <p className="text-muted-foreground text-xs">Accurate scheme & policy info</p>
              </div>
            </div>

            <div className="border-border/60 bg-card/60 flex items-center gap-3.5 rounded-2xl border p-4 shadow-sm">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
                <Headset className="size-5" />
              </div>
              <div>
                <h4 className="text-foreground text-sm font-bold">Human Escalation</h4>
                <p className="text-muted-foreground text-xs">Permission-based expert help</p>
              </div>
            </div>

            <div className="border-border/60 bg-card/60 flex items-center gap-3.5 rounded-2xl border p-4 shadow-sm">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                <Lock className="size-5" />
              </div>
              <div>
                <h4 className="text-foreground text-sm font-bold">Privacy-Aware Design</h4>
                <p className="text-muted-foreground text-xs">Zero sensitive data requested</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ======================================================== */}
      {/* FEATURES GRID SECTION                                    */}
      {/* ======================================================== */}
      <section id="features" className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-xs font-bold tracking-widest text-blue-600 uppercase dark:text-blue-400">
              POWERFUL CAPABILITIES
            </h2>
            <p className="text-foreground mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">
              Everything you need in a modern AI financial guide
            </p>
            <p className="text-muted-foreground mx-auto mt-4 max-w-2xl text-base">
              Designed with strict fintech guardrails, high-clarity voice output, and human expert
              handover.
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="group border-border/70 bg-card rounded-3xl border p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-blue-500/40 hover:shadow-xl">
              <div className="flex size-12 items-center justify-center rounded-2xl bg-blue-600/10 text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
                <HelpCircle className="size-6" />
              </div>
              <h3 className="text-foreground mt-5 text-xl font-bold">Smart Financial Guidance</h3>
              <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                Get clear, concise answers to everyday financial questions including savings
                accounts, interest calculations, EMIs, and schemes.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group border-border/70 bg-card rounded-3xl border p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-blue-500/40 hover:shadow-xl">
              <div className="flex size-12 items-center justify-center rounded-2xl bg-indigo-600/10 text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
                <FileCheck className="size-6" />
              </div>
              <h3 className="text-foreground mt-5 text-xl font-bold">Personalized Assistance</h3>
              <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                FinSahayak uses relevant user memory and domain knowledge to provide tailored
                recommendations suited to your context.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group border-border/70 bg-card rounded-3xl border p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-blue-500/40 hover:shadow-xl">
              <div className="flex size-12 items-center justify-center rounded-2xl bg-cyan-600/10 text-cyan-600 transition-colors group-hover:bg-cyan-600 group-hover:text-white">
                <Mic className="size-6" />
              </div>
              <h3 className="text-foreground mt-5 text-xl font-bold">Voice + Chat Interaction</h3>
              <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                Seamless multi-modal communication. Speak naturally with ultra-low latency voice
                synthesized via Murf Falcon TTS.
              </p>
            </div>

            {/* Feature 4 — Day 7 Highlight */}
            <div className="group relative rounded-3xl border border-amber-500/30 bg-amber-500/5 p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-amber-500/60 hover:shadow-xl dark:bg-amber-500/10">
              <span className="absolute top-4 right-4 rounded-full bg-amber-500 px-2.5 py-0.5 text-[10px] font-bold text-white uppercase">
                Day 7 Feature
              </span>
              <div className="flex size-12 items-center justify-center rounded-2xl bg-amber-500/20 text-amber-600 dark:text-amber-400">
                <Headset className="size-6" />
              </div>
              <h3 className="text-foreground mt-5 text-xl font-bold">Human Escalation</h3>
              <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                When an issue requires human review (such as possible fraud or complex loan
                reviews), FinSahayak asks your permission and creates a support request.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="group border-border/70 bg-card rounded-3xl border p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-blue-500/40 hover:shadow-xl">
              <div className="flex size-12 items-center justify-center rounded-2xl bg-emerald-600/10 text-emerald-600 transition-colors group-hover:bg-emerald-600 group-hover:text-white">
                <PhoneCall className="size-6" />
              </div>
              <h3 className="text-foreground mt-5 text-xl font-bold">Outbound Assistance</h3>
              <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                Proactive telephony alerts for critical scheme deadlines and eligibility updates
                with instant one-click opt-out support.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="group border-border/70 bg-card rounded-3xl border p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-blue-500/40 hover:shadow-xl">
              <div className="flex size-12 items-center justify-center rounded-2xl bg-rose-600/10 text-rose-600 transition-colors group-hover:bg-rose-600 group-hover:text-white">
                <Lock className="size-6" />
              </div>
              <h3 className="text-foreground mt-5 text-xl font-bold">Privacy-Aware Design</h3>
              <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                Strict data protection. Sensitive information such as OTPs, PINs, passwords, and
                CVVs are never requested or stored.
              </p>
            </div>
            {/* Feature 7 — Day 8 Analytics */}
            <div className="group relative rounded-3xl border border-violet-500/30 bg-violet-500/5 p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-violet-500/60 hover:shadow-xl dark:bg-violet-500/10">
              <span className="absolute top-4 right-4 rounded-full bg-violet-600 px-2.5 py-0.5 text-[10px] font-bold text-white uppercase">
                Day 8 Feature
              </span>
              <div className="flex size-12 items-center justify-center rounded-2xl bg-violet-500/20 text-violet-600 dark:text-violet-400">
                <BarChart3 className="size-6" />
              </div>
              <h3 className="text-foreground mt-5 text-xl font-bold">Call Analytics Dashboard</h3>
              <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                Real-time call metrics including Total Calls, Successful Calls, and Failed Calls — all
                sourced directly from the database with zero hardcoded values.
              </p>
              <Link
                href="/analytics"
                className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-violet-600 hover:underline dark:text-violet-400"
              >
                View Dashboard <ArrowRight className="size-3" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ======================================================== */}
      {/* HOW IT WORKS                                             */}
      {/* ======================================================== */}
      <section id="how-it-works" className="border-border/60 bg-muted/20 border-y py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-xs font-bold tracking-widest text-blue-600 uppercase dark:text-blue-400">
              SIMPLE & SAFE WORKFLOW
            </h2>
            <p className="text-foreground mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">
              How FinSahayak AI Works
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <div className="border-border/60 bg-card relative flex flex-col rounded-3xl border p-6 shadow-sm">
              <span className="text-4xl font-extrabold text-blue-600/30 dark:text-blue-400/30">
                01
              </span>
              <h4 className="text-foreground mt-4 text-lg font-bold">Ask</h4>
              <p className="text-muted-foreground mt-2 text-sm">
                Talk naturally with FinSahayak through voice or text chat in your preferred
                language.
              </p>
            </div>

            <div className="border-border/60 bg-card relative flex flex-col rounded-3xl border p-6 shadow-sm">
              <span className="text-4xl font-extrabold text-blue-600/30 dark:text-blue-400/30">
                02
              </span>
              <h4 className="text-foreground mt-4 text-lg font-bold">Understand</h4>
              <p className="text-muted-foreground mt-2 text-sm">
                AI analyzes your query using financial models and intent detection algorithms.
              </p>
            </div>

            <div className="border-border/60 bg-card relative flex flex-col rounded-3xl border p-6 shadow-sm">
              <span className="text-4xl font-extrabold text-blue-600/30 dark:text-blue-400/30">
                03
              </span>
              <h4 className="text-foreground mt-4 text-lg font-bold">Assist</h4>
              <p className="text-muted-foreground mt-2 text-sm">
                FinSahayak provides clear, verified financial guidance tailored to your scenario.
              </p>
            </div>

            <div className="relative flex flex-col rounded-3xl border border-amber-500/30 bg-amber-500/5 p-6 shadow-sm">
              <span className="text-4xl font-extrabold text-amber-500/30">04</span>
              <h4 className="text-foreground mt-4 text-lg font-bold">Escalate When Needed</h4>
              <p className="text-muted-foreground mt-2 text-sm">
                If human judgment is required, it asks your permission and creates a tracked support
                request.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ======================================================== */}
      {/* HUMAN SUPPORT FEATURE (DAY 7)                            */}
      {/* ======================================================== */}
      <section id="human-support" className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="via-card overflow-hidden rounded-3xl border border-blue-500/30 bg-gradient-to-br from-blue-900/10 to-indigo-900/10 p-8 shadow-xl md:p-12">
            <div className="grid grid-cols-1 items-center gap-8 lg:grid-cols-12">
              <div className="lg:col-span-7">
                <div className="inline-flex items-center gap-2 rounded-full bg-amber-500/15 px-3 py-1 text-xs font-bold text-amber-600 dark:text-amber-400">
                  <Headset className="size-3.5" />
                  <span>DAY 7 FEATURE HIGHLIGHT</span>
                </div>

                <h2 className="text-foreground mt-4 text-3xl font-extrabold tracking-tight sm:text-4xl">
                  AI knows when to ask for help.
                </h2>

                <p className="text-muted-foreground mt-4 text-base leading-relaxed sm:text-lg">
                  FinSahayak doesn't pretend to know everything. When a financial situation requires
                  human review (such as an unauthorized transaction or complex loan restructuring),
                  it asks for your permission before sharing a short, sanitized summary with human
                  support.
                </p>

                {/* Workflow diagram pills */}
                <div className="text-foreground mt-8 flex flex-wrap items-center gap-2 text-xs font-semibold">
                  <span className="border-border bg-background rounded-xl border px-3 py-1.5 shadow-sm">
                    User Problem
                  </span>
                  <span className="text-muted-foreground">→</span>
                  <span className="border-border bg-background rounded-xl border px-3 py-1.5 shadow-sm">
                    FinSahayak Detects
                  </span>
                  <span className="text-muted-foreground">→</span>
                  <span className="rounded-xl border border-amber-500/40 bg-amber-500/10 px-3 py-1.5 text-amber-600 dark:text-amber-400">
                    Explicit Permission
                  </span>
                  <span className="text-muted-foreground">→</span>
                  <span className="rounded-xl border border-blue-500/40 bg-blue-500/10 px-3 py-1.5 text-blue-600 dark:text-blue-400">
                    Support Request (FIN-2026-XXXX)
                  </span>
                  <span className="text-muted-foreground">→</span>
                  <span className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-3 py-1.5 text-emerald-600 dark:text-emerald-400">
                    Human Review
                  </span>
                </div>

                <div className="mt-8 flex items-center gap-4">
                  <Button
                    asChild
                    size="lg"
                    className="rounded-2xl bg-blue-600 font-semibold text-white hover:bg-blue-700"
                  >
                    <Link href="/assistant">Try Human Support Demo</Link>
                  </Button>
                  <Button asChild variant="outline" size="lg" className="rounded-2xl font-semibold">
                    <Link href="/escalations">View Support Dashboard</Link>
                  </Button>
                </div>
              </div>

              {/* Right Side Visual Workflow Card */}
              <div className="lg:col-span-5">
                <div className="border-border/80 bg-card rounded-2xl border p-6 shadow-md">
                  <div className="border-border/60 flex items-center justify-between border-b pb-3">
                    <span className="text-muted-foreground text-xs font-bold uppercase">
                      Sample Escalation Flow
                    </span>
                    <span className="rounded-md bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-600 dark:text-amber-400">
                      HIGH URGENCY
                    </span>
                  </div>

                  <div className="mt-4 space-y-3 text-xs">
                    <div className="bg-muted/60 rounded-xl p-3">
                      <p className="text-foreground font-semibold">User Report:</p>
                      <p className="text-muted-foreground mt-0.5">
                        "I see a payment of $450 that I did not authorize."
                      </p>
                    </div>

                    <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-3">
                      <p className="font-semibold text-blue-600 dark:text-blue-400">
                        FinSahayak Permission Prompt:
                      </p>
                      <p className="text-muted-foreground mt-0.5">
                        "I can create a support request with your name, issue summary, and follow-up
                        preference. No PINs or passwords will be included. May I proceed?"
                      </p>
                    </div>

                    <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-3">
                      <p className="font-semibold text-emerald-600 dark:text-emerald-400">
                        Generated Support Case:
                      </p>
                      <p className="text-foreground mt-0.5 font-mono text-[11px] font-bold">
                        Reference ID: FIN-2026-4821
                      </p>
                      <p className="text-muted-foreground mt-0.5">
                        Status: Open • Action: Assigned to Human Specialist
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ======================================================== */}
      {/* FOOTER                                                   */}
      {/* ======================================================== */}
      <footer className="border-border/60 bg-card/60 border-t py-12 text-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
            <div className="flex flex-col items-center gap-2 md:items-start">
              <div className="flex items-center gap-2">
                <div className="flex size-7 items-center justify-center rounded-lg bg-blue-600 text-white">
                  <Bot className="size-4" />
                </div>
                <span className="text-foreground text-lg font-bold">FinSahayak AI</span>
              </div>
              <p className="text-muted-foreground text-xs">
                "Smart Financial Guidance. Human Help When It Matters."
              </p>
            </div>

            <div className="text-muted-foreground flex flex-wrap items-center gap-6 text-xs font-medium">
              <Link href="/" className="hover:text-foreground">
                Home
              </Link>
              <Link href="/assistant" className="hover:text-foreground">
                Assistant
              </Link>
              <a href="#features" className="hover:text-foreground">
                Features
              </a>
              <Link href="/escalations" className="hover:text-foreground">
                Human Support
              </Link>
              <Link href="/analytics" className="hover:text-foreground">
                Analytics
              </Link>
              <a href="#privacy" className="hover:text-foreground">
                Privacy
              </a>
            </div>
          </div>

          <div className="border-border/40 text-muted-foreground mt-8 flex flex-col items-center justify-between gap-4 border-t pt-6 text-xs md:flex-row">
            <p>© 2026 FinSahayak AI. All rights reserved.</p>
            <p className="flex items-center gap-2">
              <span>
                Built as part of <strong>10 Days of Voice Agents</strong>
              </span>
              <span>•</span>
              <span>
                Powered by <strong>Murf Falcon TTS</strong> & <strong>LiveKit Agents</strong>
              </span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

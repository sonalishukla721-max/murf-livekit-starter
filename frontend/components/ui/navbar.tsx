'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bot, ChevronRight, Headset, Menu, ShieldCheck, X } from 'lucide-react';
import { ThemeToggle } from '@/components/app/theme-toggle';
import { Button } from '@/components/ui/button';

export function Navbar() {
  const [openCount, setOpenCount] = useState<number | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch('/api/escalations/stats');
        const json = await res.json();
        if (json.success && typeof json.data?.open === 'number') {
          setOpenCount(json.data.open + json.data.in_progress);
        }
      } catch (err) {
        console.error('Error fetching escalation count:', err);
      }
    }
    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Assistant', href: '/assistant' },
    { name: 'Features', href: '/#features' },
    { name: 'How It Works', href: '/#how-it-works' },
    { name: 'Human Support', href: '/escalations', badge: openCount },
    { name: 'About', href: '/#about' },
  ];

  return (
    <header className="border-border/40 bg-background/80 sticky top-0 z-50 w-full border-b backdrop-blur-md transition-all">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <Link
          href="/"
          className="flex items-center gap-2.5 transition-transform hover:scale-[1.02]"
        >
          <div className="flex size-9 items-center justify-center rounded-xl bg-blue-600 text-white shadow-md shadow-blue-500/20">
            <Bot className="size-5" />
          </div>
          <div className="flex flex-col">
            <span className="text-foreground font-sans text-lg font-bold tracking-tight">
              FinSahayak <span className="text-blue-600 dark:text-blue-400">AI</span>
            </span>
            <span className="text-muted-foreground text-[10px] font-medium tracking-wide uppercase">
              Financial Guidance
            </span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={`relative px-3.5 py-2 text-sm font-medium transition-colors hover:text-blue-600 ${
                  isActive ? 'font-semibold text-blue-600' : 'text-muted-foreground'
                }`}
              >
                <span className="flex items-center gap-1.5">
                  {link.name}
                  {typeof link.badge === 'number' && link.badge > 0 && (
                    <span className="inline-flex items-center justify-center rounded-full bg-amber-500/15 px-2 py-0.5 text-xs font-bold text-amber-600 dark:bg-amber-500/20 dark:text-amber-400">
                      {link.badge}
                    </span>
                  )}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Right Action Controls */}
        <div className="hidden items-center gap-3 md:flex">
          <ThemeToggle />
          <Button
            asChild
            size="sm"
            className="rounded-xl bg-blue-600 font-semibold text-white shadow-sm hover:bg-blue-700"
          >
            <Link href="/assistant">
              Try Assistant <ChevronRight className="ml-1 size-4" />
            </Link>
          </Button>
        </div>

        {/* Mobile menu trigger */}
        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="size-5" /> : <Menu className="size-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="border-border bg-background border-b px-4 pt-2 pb-6 md:hidden">
          <div className="flex flex-col gap-2">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between rounded-lg px-3 py-2 text-base font-medium transition-colors ${
                  pathname === link.href
                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400'
                    : 'text-foreground hover:bg-muted'
                }`}
              >
                <span>{link.name}</span>
                {typeof link.badge === 'number' && link.badge > 0 && (
                  <span className="rounded-full bg-amber-500 px-2 py-0.5 text-xs font-bold text-white">
                    {link.badge} open
                  </span>
                )}
              </Link>
            ))}
            <div className="mt-4 pt-2">
              <Button
                asChild
                className="w-full rounded-xl bg-blue-600 text-white hover:bg-blue-700"
              >
                <Link href="/assistant" onClick={() => setMobileMenuOpen(false)}>
                  Talk to FinSahayak AI
                </Link>
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

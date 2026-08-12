import { Bot, Headset, Mic, ShieldCheck, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="flex min-h-full flex-col items-center justify-center p-6 text-center">
      <div className="border-border/80 bg-card relative w-full max-w-md rounded-3xl border p-8 shadow-xl backdrop-blur-xl">
        <div className="mx-auto mb-5 flex size-16 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-500/30">
          <Bot className="size-8" />
        </div>

        <div className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
          <Sparkles className="size-3.5" />
          <span>FinSahayak AI Voice & Chat</span>
        </div>

        <h2 className="text-foreground text-2xl font-extrabold tracking-tight">
          Smart Financial Assistance
        </h2>

        <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
          Ask questions about savings, EMIs, loans, or request human support escalation when needed.
        </p>

        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-6 h-12 w-full rounded-2xl bg-blue-600 font-semibold text-white shadow-lg shadow-blue-600/25 transition-all hover:bg-blue-700 active:scale-[0.98]"
        >
          <Mic className="mr-2 size-5 animate-pulse" />
          {startButtonText || 'Talk to FinSahayak'}
        </Button>

        <div className="border-border/60 text-muted-foreground mt-6 flex items-center justify-center gap-4 border-t pt-4 text-xs">
          <span className="flex items-center gap-1">
            <ShieldCheck className="size-3.5 text-emerald-500" /> Safe & Private
          </span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <Headset className="size-3.5 text-amber-500" /> Day 7 Escalation
          </span>
        </div>
      </div>
    </div>
  );
};

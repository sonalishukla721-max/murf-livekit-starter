import { Suspense } from 'react';
import { headers } from 'next/headers';
import { AssistantView } from '@/components/app/assistant-view';
import { getAppConfig } from '@/lib/utils';

export default async function AssistantPage() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return (
    <Suspense
      fallback={
        <div className="bg-background flex h-[calc(100vh-4rem)] w-full items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="size-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
            <p className="text-muted-foreground text-sm font-medium">Loading FinSahayak AI…</p>
          </div>
        </div>
      }
    >
      <AssistantView appConfig={appConfig} />
    </Suspense>
  );
}

import { Suspense } from 'react';
import { LandingPage } from '@/components/app/landing-page';

export default function Page() {
  return (
    <Suspense fallback={<div className="bg-background min-h-screen" />}>
      <LandingPage />
    </Suspense>
  );
}

import { NextResponse } from 'next/server';
import { getCallAnalytics } from '@/lib/db';

export async function GET() {
  try {
    const analytics = getCallAnalytics();
    return NextResponse.json({ success: true, data: analytics });
  } catch (error: unknown) {
    console.error('[Analytics API] Error fetching call analytics:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch analytics',
      },
      { status: 500 }
    );
  }
}

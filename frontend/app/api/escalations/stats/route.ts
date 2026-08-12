import { NextResponse } from 'next/server';
import { getEscalationStats } from '@/lib/db';

export async function GET() {
  try {
    const stats = getEscalationStats();
    return NextResponse.json({ success: true, data: stats });
  } catch (error: any) {
    console.error('Error fetching escalation stats:', error);
    return NextResponse.json(
      { success: false, error: error?.message || 'Failed to fetch stats' },
      { status: 500 }
    );
  }
}

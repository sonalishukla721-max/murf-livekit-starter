import { NextResponse } from 'next/server';
import { createEscalationRecord, getEscalations } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status') || undefined;
    const urgency = searchParams.get('urgency') || undefined;
    const issue_type = searchParams.get('issue_type') || undefined;
    const search = searchParams.get('search') || undefined;

    const escalations = getEscalations({ status, urgency, issue_type, search });
    return NextResponse.json({ success: true, data: escalations });
  } catch (error: any) {
    console.error('Error fetching escalations:', error);
    return NextResponse.json(
      { success: false, error: error?.message || 'Failed to fetch escalations' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    if (!body.summary) {
      return NextResponse.json({ success: false, error: 'Summary is required' }, { status: 400 });
    }

    const newEscalation = createEscalationRecord(body);
    return NextResponse.json({ success: true, data: newEscalation }, { status: 201 });
  } catch (error: any) {
    console.error('Error creating escalation:', error);
    return NextResponse.json(
      { success: false, error: error?.message || 'Failed to create escalation' },
      { status: 500 }
    );
  }
}

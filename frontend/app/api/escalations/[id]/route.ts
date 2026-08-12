import { NextResponse } from 'next/server';
import { getEscalationById, updateEscalationStatus } from '@/lib/db';

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const escalation = getEscalationById(id);
    if (!escalation) {
      return NextResponse.json({ success: false, error: 'Escalation not found' }, { status: 404 });
    }
    return NextResponse.json({ success: true, data: escalation });
  } catch (error: any) {
    console.error('Error fetching escalation by ID:', error);
    return NextResponse.json(
      { success: false, error: error?.message || 'Failed to fetch escalation' },
      { status: 500 }
    );
  }
}

export async function PATCH(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const body = await request.json();

    if (!body.status) {
      return NextResponse.json({ success: false, error: 'Status is required' }, { status: 400 });
    }

    const updated = updateEscalationStatus(id, body.status);
    if (!updated) {
      return NextResponse.json(
        { success: false, error: 'Failed to update status or escalation not found' },
        { status: 404 }
      );
    }

    const updatedRecord = getEscalationById(id);
    return NextResponse.json({ success: true, data: updatedRecord });
  } catch (error: any) {
    console.error('Error updating escalation status:', error);
    return NextResponse.json(
      { success: false, error: error?.message || 'Failed to update escalation' },
      { status: 500 }
    );
  }
}

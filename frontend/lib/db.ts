import fs from 'fs';
import { DatabaseSync } from 'node:sqlite';
import path from 'path';

// Locate krishimitra.db in root or backend
function getDbPath(): string {
  const possiblePaths = [
    path.join(process.cwd(), '..', 'backend', 'krishimitra.db'),
    path.join(process.cwd(), 'backend', 'krishimitra.db'),
    path.join(process.cwd(), 'krishimitra.db'),
    path.resolve('..', 'backend', 'krishimitra.db'),
  ];

  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }

  // Default fallback
  const fallback = path.join(process.cwd(), '..', 'backend', 'krishimitra.db');
  return fallback;
}

export function getDb() {
  const dbPath = getDbPath();
  const db = new DatabaseSync(dbPath);

  // Ensure escalations table exists
  db.exec(`
    CREATE TABLE IF NOT EXISTS escalations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      reference_id TEXT UNIQUE NOT NULL,
      user_name TEXT NOT NULL,
      issue_type TEXT NOT NULL,
      summary TEXT NOT NULL,
      urgency TEXT NOT NULL,
      language TEXT DEFAULT 'English',
      preferred_followup TEXT DEFAULT 'Phone',
      status TEXT NOT NULL DEFAULT 'open',
      agent_checks TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  // Ensure calls table exists (created by backend on every session end)
  db.exec(`
    CREATE TABLE IF NOT EXISTS calls (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT UNIQUE NOT NULL,
      user_id TEXT DEFAULT 'anonymous',
      started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      ended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      duration INTEGER DEFAULT 0,
      channel TEXT DEFAULT 'browser',
      outcome TEXT DEFAULT 'FAILED',
      failure_type TEXT,
      success INTEGER DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  return db;
}

export interface EscalationRecord {
  id: number;
  reference_id: string;
  user_name: string;
  issue_type: string;
  summary: string;
  urgency: string;
  language: string;
  preferred_followup: string;
  status: string;
  agent_checks?: string;
  created_at: string;
  updated_at: string;
}

export function getEscalations(filters: {
  status?: string;
  urgency?: string;
  issue_type?: string;
  search?: string;
}): EscalationRecord[] {
  const db = getDb();
  let query = 'SELECT * FROM escalations WHERE 1=1';
  const params: (string | number)[] = [];

  if (filters.status && filters.status.toLowerCase() !== 'all') {
    query += ' AND status = ?';
    params.push(filters.status.toLowerCase());
  }

  if (filters.urgency && filters.urgency.toLowerCase() !== 'all') {
    query += ' AND urgency = ?';
    params.push(filters.urgency.toLowerCase());
  }

  if (filters.issue_type && filters.issue_type.toLowerCase() !== 'all') {
    query += ' AND issue_type LIKE ?';
    params.push(`%${filters.issue_type}%`);
  }

  if (filters.search) {
    query += ' AND (reference_id LIKE ? OR user_name LIKE ? OR summary LIKE ?)';
    params.push(`%${filters.search}%`, `%${filters.search}%`, `%${filters.search}%`);
  }

  query += ' ORDER BY created_at DESC';

  const stmt = db.prepare(query);
  const rows = stmt.all(...params) as unknown as EscalationRecord[];
  db.close();
  return rows;
}

export function getEscalationById(idOrRef: string): EscalationRecord | null {
  const db = getDb();
  let stmt;
  if (/^\d+$/.test(idOrRef)) {
    stmt = db.prepare('SELECT * FROM escalations WHERE id = ?');
    const row = stmt.get(Number(idOrRef)) as unknown as EscalationRecord | undefined;
    db.close();
    return row || null;
  } else {
    stmt = db.prepare('SELECT * FROM escalations WHERE reference_id = ?');
    const row = stmt.get(idOrRef) as unknown as EscalationRecord | undefined;
    db.close();
    return row || null;
  }
}

export function updateEscalationStatus(idOrRef: string, newStatus: string): boolean {
  const db = getDb();
  const now = new Date().toISOString();
  let stmt;
  let result;

  if (/^\d+$/.test(idOrRef)) {
    stmt = db.prepare('UPDATE escalations SET status = ?, updated_at = ? WHERE id = ?');
    result = stmt.run(newStatus.toLowerCase(), now, Number(idOrRef));
  } else {
    stmt = db.prepare('UPDATE escalations SET status = ?, updated_at = ? WHERE reference_id = ?');
    result = stmt.run(newStatus.toLowerCase(), now, idOrRef);
  }

  db.close();
  return (result.changes ?? 0) > 0;
}

export function getEscalationStats() {
  const db = getDb();

  const totalRow = db.prepare('SELECT COUNT(*) as count FROM escalations').get() as {
    count: number;
  };
  const openRow = db
    .prepare("SELECT COUNT(*) as count FROM escalations WHERE status = 'open'")
    .get() as { count: number };
  const inProgressRow = db
    .prepare("SELECT COUNT(*) as count FROM escalations WHERE status = 'in_progress'")
    .get() as { count: number };
  const resolvedRow = db
    .prepare("SELECT COUNT(*) as count FROM escalations WHERE status = 'resolved'")
    .get() as { count: number };
  const highRow = db
    .prepare(
      "SELECT COUNT(*) as count FROM escalations WHERE urgency IN ('high', 'emergency') AND status != 'resolved'"
    )
    .get() as { count: number };

  db.close();

  return {
    total: totalRow.count,
    open: openRow.count,
    in_progress: inProgressRow.count,
    resolved: resolvedRow.count,
    high_priority: highRow.count,
  };
}

export function createEscalationRecord(data: {
  user_name?: string;
  issue_type?: string;
  summary: string;
  urgency?: string;
  language?: string;
  preferred_followup?: string;
}): EscalationRecord {
  const db = getDb();
  const year = new Date().getFullYear();
  const rand = Math.floor(1000 + Math.random() * 9000);
  const reference_id = `FIN-${year}-${rand}`;
  const now = new Date().toISOString();

  const user_name = data.user_name || 'Valued Customer';
  const issue_type = data.issue_type || 'General Financial Issue';
  const urgency = data.urgency || 'medium';
  const language = data.language || 'English';
  const preferred_followup = data.preferred_followup || 'Phone';
  const summary = data.summary;
  const agent_checks = issue_type.toLowerCase().includes('fraud')
    ? 'FinSahayak identified the report as a possible unauthorized transaction and did not make unsupported claims about the account.'
    : 'FinSahayak gathered case summary and verified user permission before creating human support request.';

  const stmt = db.prepare(`
    INSERT INTO escalations (reference_id, user_name, issue_type, summary, urgency, language, preferred_followup, status, agent_checks, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
  `);

  stmt.run(
    reference_id,
    user_name,
    issue_type,
    summary,
    urgency,
    language,
    preferred_followup,
    agent_checks,
    now,
    now
  );

  const created = getEscalationById(reference_id);
  db.close();

  if (!created) {
    throw new Error('Failed to retrieve newly created escalation');
  }

  return created;
}

// ============================================================
// CALL ANALYTICS (Day 8)
// ============================================================

export interface CallRecord {
  id: number;
  session_id: string;
  user_id: string;
  started_at: string;
  ended_at: string;
  duration: number;
  channel: string;
  outcome: string;
  failure_type: string | null;
  success: number;
  created_at: string;
}

export interface CallAnalytics {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  recent_calls: CallRecord[];
}

export function getCallAnalytics(): CallAnalytics {
  const db = getDb();

  const totalRow = db.prepare('SELECT COUNT(*) as cnt FROM calls').get() as { cnt: number };
  const successRow = db.prepare('SELECT COUNT(*) as cnt FROM calls WHERE success = 1').get() as {
    cnt: number;
  };
  const failedRow = db.prepare('SELECT COUNT(*) as cnt FROM calls WHERE success = 0').get() as {
    cnt: number;
  };

  const recentRows = db
    .prepare(
      'SELECT id, session_id, user_id, started_at, ended_at, duration, channel, outcome, failure_type, success, created_at FROM calls ORDER BY created_at DESC LIMIT 20'
    )
    .all() as unknown as CallRecord[];

  db.close();

  return {
    total_calls: totalRow.cnt,
    successful_calls: successRow.cnt,
    failed_calls: failedRow.cnt,
    recent_calls: recentRows,
  };
}

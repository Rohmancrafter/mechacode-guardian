// API client for the MechaCode Guardian backend.
//
// Architecture §1.1: "REST calls to the FastAPI backend over HTTP.
//  No direct calls to external AI services."
//
// The Vite dev proxy (vite.config.ts) forwards /api/* to localhost:8000,
// so the base URL is empty in development.

const API_BASE = '';

// ---------------------------------------------------------------------------
// Types mirroring backend/api/schemas.py
// ---------------------------------------------------------------------------

export type Language = 'id' | 'en';

export type ConfidenceBand = 'High' | 'Medium' | 'Low';

export interface DiagnoseRequest {
  equipment_type: string;
  manufacturer?: string;
  model?: string;
  alarm_code?: string;
  symptom_text: string;
  language?: Language;
}

export interface EscalationTrigger {
  pattern: string;
  hazard_type: string;
  severity: string;
  matched_text: string;
}

export interface ProbableCause {
  rank: number;
  description: string;
  evidence_indices: number[];
  confidence_band: ConfidenceBand;
}

export interface ChecklistStep {
  step_number: number;
  action: string;
  tool_required?: string;
  safety_note?: string;
  expected_outcome?: string;
  evidence_indices: number[];
}

export interface CitationBadge {
  evidence_index: number;
  source_doc: string;
  page_start?: number;
  page_end?: number;
  section_title?: string;
}

export interface DiagnoseResponse {
  session_id: string;
  language: Language;
  escalation_flag: boolean;
  escalation_triggers: EscalationTrigger[];
  escalation_message?: string;
  causes?: ProbableCause[];
  checklist?: ChecklistStep[];
  confidence_band?: ConfidenceBand;
  citations?: CitationBadge[];
  refusal_flag: boolean;
  refusal_message?: string;
  provider_used: string;
  fallback_used: boolean;
  disclaimer: string;
}

export interface ReportResponse {
  session_id: string;
  markdown: string;
  filename: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  services: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Request helpers
// ---------------------------------------------------------------------------

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API error ${response.status}: ${detail}`);
  }

  return response.json() as Promise<T>;
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Public API functions
// ---------------------------------------------------------------------------

/** Submit a symptom description and receive a diagnosis (FR-01, FR-03, FR-04). */
export async function submitDiagnosis(
  request: DiagnoseRequest,
): Promise<DiagnoseResponse> {
  return post<DiagnoseResponse>('/api/v1/diagnose', request);
}

/** Generate and fetch the Markdown diagnosis report for a session (FR-07). */
export async function generateReport(sessionId: string): Promise<ReportResponse> {
  return post<ReportResponse>(`/api/v1/report/${sessionId}`, {});
}

/** Fetch application health status. */
export async function fetchHealth(): Promise<HealthResponse> {
  return get<HealthResponse>('/health');
}

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import SymptomForm from '../components/SymptomForm';
import EscalationNotice from '../components/EscalationNotice';
import DiagnosisResult from '../components/DiagnosisResult';
import Checklist from '../components/Checklist';
import ReportDownload from '../components/ReportDownload';
import { submitDiagnosis } from '../api/client';
import type { DiagnoseRequest, DiagnoseResponse } from '../api/client';

/**
 * DiagnosisPage — primary user journey (PRD §4, User Journey).
 *
 * Renders:
 *  - SymptomForm (input)
 *  - EscalationNotice (when escalation_flag = true — topmost, non-dismissable)
 *  - DiagnosisResult + Checklist + ReportDownload (when safe to proceed)
 *  - Refusal notice (when refusal_flag = true)
 */
const DiagnosisPage: React.FC = () => {
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<DiagnoseResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (request: DiagnoseRequest) => {
    setIsLoading(true);
    setResponse(null);
    setErrorMessage(null);

    try {
      const result = await submitDiagnosis(request);
      setResponse(result);
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : t('error.generic'),
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: '760px', margin: '0 auto', padding: '1.5rem' }}>
      <header style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ margin: '0 0 0.25rem' }}>{t('app.title')}</h1>
        <p style={{ margin: 0, color: '#57606a' }}>{t('app.tagline')}</p>
      </header>

      {/* Escalation notice — topmost priority (SR-03) */}
      {response?.escalation_flag && (
        <EscalationNotice
          escalationMessage={response.escalation_message}
          hazardTypes={response.escalation_triggers.map(tr => tr.hazard_type)}
        />
      )}

      {/* Symptom input form */}
      <SymptomForm onSubmit={(req) => void handleSubmit(req)} isLoading={isLoading} />

      {/* Loading state */}
      {isLoading && (
        <p aria-live="polite" style={{ marginTop: '1rem', color: '#57606a' }}>
          {t('diagnosis.loading')}
        </p>
      )}

      {/* Error state */}
      {errorMessage && (
        <div role="alert" style={{ color: '#b91c1c', marginTop: '1rem' }}>
          {errorMessage}
        </div>
      )}

      {/* Refusal notice (SR-06) */}
      {response && !response.escalation_flag && response.refusal_flag && (
        <div
          role="status"
          style={{
            marginTop: '1.5rem',
            padding: '1rem',
            background: '#f7f8fa',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
          }}
        >
          <h3 style={{ margin: '0 0 0.5rem' }}>{t('refusal.title')}</h3>
          <p style={{ margin: 0 }}>
            {response.refusal_message ?? t('refusal.message')}
          </p>
        </div>
      )}

      {/* Diagnosis result — only when safe (no escalation, no refusal) */}
      {response && !response.escalation_flag && !response.refusal_flag && (
        <>
          <div style={{ marginTop: '1.5rem' }}>
            <DiagnosisResult response={response} />
          </div>

          {response.checklist && response.checklist.length > 0 && (
            <Checklist steps={response.checklist} />
          )}

          <ReportDownload sessionId={response.session_id} />
        </>
      )}
    </main>
  );
};

export default DiagnosisPage;

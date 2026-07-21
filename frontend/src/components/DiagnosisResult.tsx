import React from 'react';
import { useTranslation } from 'react-i18next';
import type { DiagnoseResponse } from '../api/client';

interface DiagnosisResultProps {
  response: DiagnoseResponse;
}

/**
 * DiagnosisResult — displays ranked probable causes and citations (FR-04).
 *
 * Shown only when escalation_flag is false and refusal_flag is false.
 * Always renders the disclaimer (SR-04).
 */
const DiagnosisResult: React.FC<DiagnosisResultProps> = ({ response }) => {
  const { t } = useTranslation();

  return (
    <div>
      {/* Confidence band */}
      {response.confidence_band && (
        <p style={{ marginBottom: '0.75rem' }}>
          <strong>{t('diagnosis.confidence')}:</strong> {response.confidence_band}
          {response.fallback_used && (
            <span style={{ marginLeft: '0.5rem', fontSize: '0.8rem', color: '#57606a' }}>
              (via fallback provider)
            </span>
          )}
        </p>
      )}

      {/* Probable causes */}
      {response.causes && response.causes.length > 0 && (
        <section aria-labelledby="causes-heading">
          <h3 id="causes-heading">{t('diagnosis.causes.title')}</h3>
          <ol>
            {response.causes.map(cause => (
              <li key={cause.rank} style={{ marginBottom: '0.75rem' }}>
                <strong>{t('diagnosis.cause.rank', { rank: cause.rank })}</strong>
                <p style={{ margin: '0.25rem 0' }}>{cause.description}</p>

                {/* Citations */}
                {cause.evidence_indices.length > 0 && response.citations && (
                  <div style={{ fontSize: '0.875rem', color: '#57606a' }}>
                    {cause.evidence_indices.map(idx => {
                      const citation = response.citations?.find(c => c.evidence_index === idx);
                      if (!citation) return null;
                      return (
                        <span
                          key={idx}
                          title={`${citation.source_doc}${citation.page_start ? `, p.${citation.page_start}` : ''}`}
                          style={{
                            display: 'inline-block',
                            marginRight: '0.5rem',
                            padding: '0.1rem 0.4rem',
                            background: '#f0f4ff',
                            border: '1px solid #3b82d4',
                            borderRadius: '0.25rem',
                          }}
                        >
                          [{t('diagnosis.citation')}: {citation.source_doc}
                          {citation.page_start ? `, p.${citation.page_start}` : ''}
                          {citation.section_title ? `, §${citation.section_title}` : ''}]
                        </span>
                      );
                    })}
                  </div>
                )}
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* SR-04 disclaimer */}
      <p
        style={{
          marginTop: '1.5rem',
          fontSize: '0.8rem',
          color: '#57606a',
          borderTop: '1px solid #e5e7eb',
          paddingTop: '0.75rem',
        }}
      >
        {response.disclaimer}
      </p>
    </div>
  );
};

export default DiagnosisResult;

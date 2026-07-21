import React from 'react';
import { useTranslation } from 'react-i18next';
import type { ChecklistStep } from '../api/client';

interface ChecklistProps {
  steps: ChecklistStep[];
}

/**
 * Checklist — ordered inspection steps (FR-06).
 *
 * Rendered only when escalation_flag is false.
 * Safety notes are prominently displayed (SR-05, FR-06.2).
 */
const Checklist: React.FC<ChecklistProps> = ({ steps }) => {
  const { t } = useTranslation();

  if (steps.length === 0) return null;

  return (
    <section aria-labelledby="checklist-heading" style={{ marginTop: '1.5rem' }}>
      <h3 id="checklist-heading">{t('diagnosis.checklist.title')}</h3>
      <ol style={{ paddingLeft: '1.25rem' }}>
        {steps.map(step => (
          <li key={step.step_number} style={{ marginBottom: '1rem' }}>
            <p style={{ fontWeight: 600, margin: '0 0 0.25rem' }}>
              {step.step_number}. {step.action}
            </p>

            {step.tool_required && (
              <p style={{ margin: '0.125rem 0', fontSize: '0.875rem', color: '#57606a' }}>
                Tool: {step.tool_required}
              </p>
            )}

            {/* Safety note — prominently displayed (SR-05) */}
            {step.safety_note && (
              <div
                role="alert"
                style={{
                  background: '#fffbeb',
                  border: '1px solid #f59e0b',
                  borderRadius: '0.25rem',
                  padding: '0.5rem 0.75rem',
                  margin: '0.375rem 0',
                  fontSize: '0.875rem',
                  color: '#92400e',
                }}
              >
                <strong>{t('diagnosis.checklist.safety_note')}: </strong>
                {step.safety_note}
              </div>
            )}

            {step.expected_outcome && (
              <p style={{ margin: '0.125rem 0', fontSize: '0.875rem' }}>
                Expected: {step.expected_outcome}
              </p>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
};

export default Checklist;

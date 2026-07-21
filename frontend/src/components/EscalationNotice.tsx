import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * EscalationNotice — non-dismissable safety alert (SR-02, SR-03, FR-05.2/5.3).
 *
 * MUST be the topmost, highest-visual-priority element on the page when active.
 * Cannot be clicked through or dismissed.
 */
interface EscalationNoticeProps {
  escalationMessage?: string;
  hazardTypes?: string[];
}

const EscalationNotice: React.FC<EscalationNoticeProps> = ({
  escalationMessage,
  hazardTypes = [],
}) => {
  const { t } = useTranslation();

  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        background: '#b91c1c',
        color: '#ffffff',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        border: '4px solid #7f1d1d',
        marginBottom: '1.5rem',
      }}
    >
      <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.25rem', fontWeight: 700 }}>
        {t('escalation.title')}
      </h2>
      <p style={{ margin: '0 0 0.5rem' }}>{t('escalation.subtitle')}</p>

      {escalationMessage && (
        <p style={{ margin: '0.5rem 0', fontWeight: 600 }}>{escalationMessage}</p>
      )}

      {hazardTypes.length > 0 && (
        <p style={{ margin: '0.5rem 0', fontSize: '0.875rem' }}>
          Hazards: {hazardTypes.join(', ')}
        </p>
      )}
    </div>
  );
};

export default EscalationNotice;

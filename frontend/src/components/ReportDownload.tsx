import React from 'react';
import { useTranslation } from 'react-i18next';
import type { ReportResponse } from '../api/client';
import { generateReport } from '../api/client';

interface ReportDownloadProps {
  sessionId: string;
}

/**
 * ReportDownload — triggers report generation and offers a Markdown download (FR-07).
 */
const ReportDownload: React.FC<ReportDownloadProps> = ({ sessionId }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleDownload = async () => {
    setLoading(true);
    setError(null);

    try {
      const report: ReportResponse = await generateReport(sessionId);

      // Trigger browser download of the Markdown content
      const blob = new Blob([report.markdown], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = report.filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('error.generic'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: '1.5rem' }}>
      <button
        type="button"
        onClick={() => void handleDownload()}
        disabled={loading}
        style={{ padding: '0.625rem 1.25rem', cursor: 'pointer' }}
      >
        {loading ? '...' : t('diagnosis.report.download')}
      </button>
      {error && (
        <p style={{ color: '#b91c1c', marginTop: '0.5rem', fontSize: '0.875rem' }}>{error}</p>
      )}
    </div>
  );
};

export default ReportDownload;

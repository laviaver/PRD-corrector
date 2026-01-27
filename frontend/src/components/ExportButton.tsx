import { useState } from 'react';
import { exportAnalysis } from '../services/exportService';
import { formatError, logError } from '../utils/errorHandler';
import './ExportButton.css';

interface ExportButtonProps {
  analysisId: string;
  format?: 'pdf' | 'markdown' | 'json';
}

export default function ExportButton({ analysisId, format = 'markdown' }: ExportButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleExport = async () => {
    setLoading(true);
    setError('');

    try {
      const result = await exportAnalysis(analysisId, format);
      // In production, trigger file download
      alert(`Export created: ${result.file_path}\n${result.message}`);
    } catch (err) {
      const errorMessage = formatError(err);
      setError(errorMessage);
      logError(err, 'ExportButton.handleExport');
    } finally {
      setLoading(false);
    }
  };

  const formatLabels: Record<string, string> = {
    pdf: 'PDF',
    markdown: 'Markdown',
    json: 'JSON',
  };

  return (
    <div className="export-button-container">
      <button
        onClick={handleExport}
        disabled={loading}
        className="btn-export"
      >
        {loading ? 'Exporting...' : `Export as ${formatLabels[format]}`}
      </button>
      {error && (
        <div className="export-error">
          {error}
        </div>
      )}
    </div>
  );
}

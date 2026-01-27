import { useEffect, useState } from 'react';
import { getAnalysisStatus, AnalysisStatus as AnalysisStatusType } from '../services/analysisService';
import './AnalysisStatus.css';

interface AnalysisStatusProps {
  analysisId: string;
  onComplete?: () => void;
  pollInterval?: number;
}

export default function AnalysisStatus({
  analysisId,
  onComplete,
  pollInterval = 2000,
}: AnalysisStatusProps) {
  const [status, setStatus] = useState<AnalysisStatusType | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        const currentStatus = await getAnalysisStatus(analysisId);
        setStatus(currentStatus);

        if (currentStatus.status === 'completed') {
          onComplete?.();
          if (intervalId) clearInterval(intervalId);
        } else if (currentStatus.status === 'failed') {
          setError(currentStatus.error_message || 'Analysis failed');
          if (intervalId) clearInterval(intervalId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get analysis status');
        if (intervalId) clearInterval(intervalId);
      }
    };

    // Poll immediately
    pollStatus();

    // Then poll at interval
    intervalId = setInterval(pollStatus, pollInterval);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [analysisId, onComplete, pollInterval]);

  if (error) {
    return (
      <div className="analysis-status error">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  if (!status) {
    return <div className="analysis-status">Loading status...</div>;
  }

  const statusMessages = {
    pending: 'Analysis queued...',
    processing: 'Analyzing PRD...',
    completed: 'Analysis completed!',
    failed: 'Analysis failed',
  };

  return (
    <div className={`analysis-status ${status.status}`}>
      <div className="status-indicator">
        {status.status === 'processing' && <span className="spinner" />}
        <span className="status-text">{statusMessages[status.status]}</span>
      </div>
      {status.status === 'processing' && (
        <div className="status-details">
          <p>This may take up to 30 seconds...</p>
        </div>
      )}
    </div>
  );
}

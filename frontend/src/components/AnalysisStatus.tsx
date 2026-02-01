import { useCallback, useEffect, useRef, useState } from 'react';
import { getAnalysisStatus, AnalysisStatus as AnalysisStatusType } from '../services/analysisService';
import './AnalysisStatus.css';

const POLL_INTERVAL_MS = 1500;
const STUCK_TIMEOUT_MS = 60000; // Show "taking longer" after 60s

interface AnalysisStatusProps {
  analysisId: string;
  onComplete?: () => void;
  onBack?: () => void;
  pollInterval?: number;
}

export default function AnalysisStatus({
  analysisId,
  onComplete,
  onBack,
  pollInterval = POLL_INTERVAL_MS,
}: AnalysisStatusProps) {
  const [status, setStatus] = useState<AnalysisStatusType | null>(null);
  const [error, setError] = useState<string>('');
  const [stuck, setStuck] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const startTimeRef = useRef<number>(Date.now());
  const intervalIdRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalIdRef.current) {
      clearInterval(intervalIdRef.current);
      intervalIdRef.current = null;
    }
  }, []);

  useEffect(() => {
    startTimeRef.current = Date.now();
    setStuck(false);
    setElapsed(0);

    const pollStatus = async () => {
      try {
        const currentStatus = await getAnalysisStatus(analysisId);
        setStatus(currentStatus);

        if (currentStatus.status === 'completed') {
          stopPolling();
          onComplete?.();
        } else if (currentStatus.status === 'failed') {
          stopPolling();
          setError(currentStatus.error_message || 'Analysis failed');
        } else if (Date.now() - startTimeRef.current >= STUCK_TIMEOUT_MS) {
          setStuck(true);
        }
      } catch (err) {
        stopPolling();
        setError(err instanceof Error ? err.message : 'Failed to get analysis status');
      }
    };

    pollStatus();
    intervalIdRef.current = setInterval(pollStatus, pollInterval);

    return () => stopPolling();
  }, [analysisId, onComplete, pollInterval, stopPolling]);

  useEffect(() => {
    const inProgress = status?.status === 'processing' || status?.status === 'pending' || status?.status === 'converting';
    if (!inProgress) return;
    const t = setInterval(() => {
      setElapsed(Math.round((Date.now() - startTimeRef.current) / 1000));
    }, 1000);
    return () => clearInterval(t);
  }, [status?.status]);

  if (error) {
    return (
      <div className="analysis-status error">
        <strong>Error:</strong> {error}
        {onBack && (
          <button type="button" className="btn-back-inline" onClick={onBack}>
            Back to Upload
          </button>
        )}
      </div>
    );
  }

  if (stuck && status && (status.status === 'processing' || status.status === 'pending' || status.status === 'converting')) {
    return (
      <div className="analysis-status stuck">
        <strong>Taking longer than expected</strong>
        <p>The analysis may have failed or the server is slow. You can try again or go back.</p>
        {onBack && (
          <button type="button" className="btn-back-inline" onClick={onBack}>
            Back to Upload
          </button>
        )}
      </div>
    );
  }

  if (!status) {
    return <div className="analysis-status">Loading status...</div>;
  }

  const statusMessages: Record<string, string> = {
    converting: 'Converting file to text...',
    pending: 'Analysis queued...',
    processing: 'Analyzing PRD...',
    completed: 'Analysis completed!',
    failed: 'Analysis failed',
  };

  return (
    <div className={`analysis-status ${status.status}`}>
      <div className="status-indicator">
        {(status.status === 'processing' || status.status === 'converting') && <span className="spinner" />}
        <span className="status-text">{statusMessages[status.status] ?? status.status}</span>
      </div>
      {(status.status === 'processing' || status.status === 'pending' || status.status === 'converting') && (
        <div className="status-details">
          <p>This usually takes 10–30 seconds.{elapsed > 0 && ` Elapsed: ${elapsed}s`}</p>
        </div>
      )}
    </div>
  );
}

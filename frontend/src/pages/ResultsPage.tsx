import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AnalysisStatus from '../components/AnalysisStatus';
import SuggestionList from '../components/SuggestionList';
import AnalysisSummary from '../components/AnalysisSummary';
import ExportButton from '../components/ExportButton';
import { getAnalysis, AnalysisResult } from '../services/analysisService';
import { formatError, logError } from '../utils/errorHandler';
import './ResultsPage.css';

export default function ResultsPage() {
  const { prdId } = useParams<{ prdId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!prdId) {
      setError('PRD ID is required');
      setLoading(false);
      return;
    }

    // We need to get the analysis ID from the PRD
    // For now, we'll use the PRD ID as a placeholder
    // In a real implementation, we'd fetch the analysis ID from the PRD
    loadAnalysis(prdId);
  }, [prdId]);

  const loadAnalysis = async (analysisId: string) => {
    try {
      setLoading(true);
      const result = await getAnalysis(analysisId);
      setAnalysis(result);
      setError('');
    } catch (err) {
      const errorMessage = formatError(err);
      setError(errorMessage);
      logError(err, 'ResultsPage.loadAnalysis');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysisComplete = () => {
    if (prdId) {
      loadAnalysis(prdId);
    }
  };

  if (loading && !analysis) {
    return (
      <div className="results-page">
        <div className="loading">Loading analysis...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-page">
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
        <button onClick={() => navigate('/')} className="btn-back">
          Back to Upload
        </button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="results-page">
        <div className="error-message">Analysis not found</div>
        <button onClick={() => navigate('/')} className="btn-back">
          Back to Upload
        </button>
      </div>
    );
  }

  const { analysis: analysisData, suggestions } = analysis;

  return (
    <div className="results-page">
      <div className="results-header">
        <h1>PRD Analysis Results</h1>
        <button onClick={() => navigate('/')} className="btn-back">
          Analyze Another PRD
        </button>
      </div>

      {analysisData.status === 'processing' || analysisData.status === 'pending' ? (
        <div className="analysis-in-progress">
          <AnalysisStatus
            analysisId={analysisData.id}
            onComplete={handleAnalysisComplete}
          />
        </div>
      ) : (
        <>
          {analysisData.summary && (
            <AnalysisSummary
              totalSuggestions={analysisData.summary.total_suggestions}
              suggestionsByCategory={analysisData.summary.suggestions_by_category}
              suggestionsByPriority={analysisData.summary.suggestions_by_priority}
            />
          )}

          <div className="export-section">
            <ExportButton analysisId={analysisData.id} format="markdown" />
            <ExportButton analysisId={analysisData.id} format="json" />
          </div>

          <div className="suggestions-section">
            <h2>Suggestions</h2>
            <SuggestionList suggestions={suggestions} groupBy="category" />
          </div>
        </>
      )}
    </div>
  );
}

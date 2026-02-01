import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AnalysisStatus from '../components/AnalysisStatus';
import SuggestionList from '../components/SuggestionList';
import AnalysisSummary from '../components/AnalysisSummary';
import ExportButton from '../components/ExportButton';
import { getAnalysis, getAnalysisByPRD, AnalysisResult } from '../services/analysisService';
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
      setError('Analysis ID is required');
      setLoading(false);
      return;
    }

    // Try to load as analysis_id first, then fallback to PRD ID lookup
    loadAnalysis(prdId);
  }, [prdId]);

  const loadAnalysis = async (id: string) => {
    try {
      setLoading(true);
      // First try as analysis_id
      let result: AnalysisResult;
      try {
        result = await getAnalysis(id);
      } catch (err) {
        // If not found, try as PRD ID
        result = await getAnalysisByPRD(id);
      }
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
      // prdId is actually analysis_id
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

      {analysisData.status === 'processing' || analysisData.status === 'pending' || analysisData.status === 'converting' ? (
        <div className="analysis-in-progress">
          <AnalysisStatus
            analysisId={analysisData.id}
            onComplete={handleAnalysisComplete}
            onBack={() => navigate('/')}
          />
        </div>
      ) : (
        <>
          {analysisData.scores && (
            <div className="scores-section" data-testid="scores-section">
              <h2>PRD Scores</h2>
              <div className="scores-grid">
                <div className="score-item">
                  <span className="score-label">Structure</span>
                  <span className="score-value">{analysisData.scores.structure_score}/100</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Completeness</span>
                  <span className="score-value">{analysisData.scores.completeness_score}/100</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Total</span>
                  <span className="score-value score-total">{analysisData.scores.total_score}/100</span>
                </div>
              </div>
            </div>
          )}

          {analysisData.incomplete_sections && analysisData.incomplete_sections.length > 0 && (
            <div className="incomplete-sections" data-testid="incomplete-sections">
              <strong>Review incomplete for:</strong>{' '}
              {analysisData.incomplete_sections.join(', ')}
            </div>
          )}

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

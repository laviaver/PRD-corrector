import './AnalysisSummary.css';

interface AnalysisSummaryProps {
  totalSuggestions: number;
  suggestionsByCategory: Record<string, number>;
  suggestionsByPriority: Record<string, number>;
}

export default function AnalysisSummary({
  totalSuggestions,
  suggestionsByCategory,
  suggestionsByPriority,
}: AnalysisSummaryProps) {
  const categoryLabels: Record<string, string> = {
    structure: 'Structure',
    clarity: 'Clarity',
    completeness: 'Completeness',
    best_practices: 'Best Practices',
    technical_quality: 'Technical Quality',
  };

  return (
    <div className="analysis-summary">
      <h2>Analysis Summary</h2>
      <div className="summary-grid">
        <div className="summary-item">
          <div className="summary-label">Total Suggestions</div>
          <div className="summary-value">{totalSuggestions}</div>
        </div>

        <div className="summary-item">
          <div className="summary-label">By Priority</div>
          <div className="summary-details">
            <span className="priority-high">
              High: {suggestionsByPriority.high || 0}
            </span>
            <span className="priority-medium">
              Medium: {suggestionsByPriority.medium || 0}
            </span>
            <span className="priority-low">
              Low: {suggestionsByPriority.low || 0}
            </span>
          </div>
        </div>

        <div className="summary-item full-width">
          <div className="summary-label">By Category</div>
          <div className="category-list">
            {Object.entries(suggestionsByCategory).map(([category, count]) => (
              <span key={category} className="category-item">
                {categoryLabels[category] || category}: {count}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

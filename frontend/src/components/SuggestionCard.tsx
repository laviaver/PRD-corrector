import { Suggestion } from '../services/analysisService';
import './SuggestionCard.css';

interface SuggestionCardProps {
  suggestion: Suggestion;
}

export default function SuggestionCard({ suggestion }: SuggestionCardProps) {
  const priorityColors: Record<string, string> = {
    high: '#dc3545',
    medium: '#ffc107',
    low: '#28a745',
  };

  const categoryLabels: Record<string, string> = {
    structure: 'Structure',
    clarity: 'Clarity',
    completeness: 'Completeness',
    best_practices: 'Best Practices',
    technical_quality: 'Technical Quality',
  };

  return (
    <div className={`suggestion-card priority-${suggestion.priority}`}>
      <div className="suggestion-header">
        <div className="suggestion-title-row">
          <h3 className="suggestion-title">{suggestion.title}</h3>
          <div className="suggestion-badges">
            <span
              className="priority-badge"
              style={{ backgroundColor: priorityColors[suggestion.priority] }}
            >
              {suggestion.priority.toUpperCase()}
            </span>
            <span className="category-badge">
              {categoryLabels[suggestion.category] || suggestion.category}
            </span>
          </div>
        </div>
      </div>

      <div className="suggestion-details">
        <div className="explanation">
          <strong>Explanation:</strong>
          <p>{suggestion.explanation}</p>
        </div>

        {suggestion.location && (
          <div className="location">
            <strong>Location:</strong>
            <p>
              {suggestion.location.section && `Section: ${suggestion.location.section}`}
              {suggestion.location.paragraph_index !== undefined &&
                `, Paragraph ${suggestion.location.paragraph_index + 1}`}
            </p>
          </div>
        )}

        {suggestion.example && (
          <div className="example">
            <strong>Example:</strong>
            <pre>{suggestion.example}</pre>
          </div>
        )}

        {suggestion.template && (
          <div className="template">
            <strong>Template:</strong>
            <pre>{suggestion.template}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

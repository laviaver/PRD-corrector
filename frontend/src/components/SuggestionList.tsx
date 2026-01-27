import { Suggestion } from '../services/analysisService';
import SuggestionCard from './SuggestionCard';
import './SuggestionList.css';

interface SuggestionListProps {
  suggestions: Suggestion[];
  groupBy?: 'category' | 'priority' | 'none';
}

export default function SuggestionList({
  suggestions,
  groupBy = 'category',
}: SuggestionListProps) {
  if (suggestions.length === 0) {
    return (
      <div className="suggestion-list empty">
        <p>No suggestions found. Your PRD looks good!</p>
      </div>
    );
  }

  if (groupBy === 'none') {
    return (
      <div className="suggestion-list">
        {suggestions.map((suggestion) => (
          <SuggestionCard key={suggestion.id} suggestion={suggestion} />
        ))}
      </div>
    );
  }

  if (groupBy === 'category') {
    const grouped = suggestions.reduce((acc, suggestion) => {
      const category = suggestion.category;
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(suggestion);
      return acc;
    }, {} as Record<string, Suggestion[]>);

    const categoryLabels: Record<string, string> = {
      structure: 'Structure & Organization',
      clarity: 'Clarity',
      completeness: 'Completeness',
      best_practices: 'Best Practices',
      technical_quality: 'Technical Quality',
    };

    return (
      <div className="suggestion-list grouped">
        {Object.entries(grouped).map(([category, categorySuggestions]) => (
          <div key={category} className="suggestion-group">
            <h2 className="group-title">
              {categoryLabels[category] || category} ({categorySuggestions.length})
            </h2>
            {categorySuggestions.map((suggestion) => (
              <SuggestionCard key={suggestion.id} suggestion={suggestion} />
            ))}
          </div>
        ))}
      </div>
    );
  }

  // Group by priority
  const grouped = suggestions.reduce((acc, suggestion) => {
    const priority = suggestion.priority;
    if (!acc[priority]) {
      acc[priority] = [];
    }
    acc[priority].push(suggestion);
    return acc;
  }, {} as Record<string, Suggestion[]>);

  const priorityOrder = ['high', 'medium', 'low'];
  const priorityLabels: Record<string, string> = {
    high: 'High Priority',
    medium: 'Medium Priority',
    low: 'Low Priority',
  };

  return (
    <div className="suggestion-list grouped">
      {priorityOrder.map((priority) => {
        if (!grouped[priority]) return null;
        return (
          <div key={priority} className="suggestion-group">
            <h2 className="group-title">
              {priorityLabels[priority]} ({grouped[priority].length})
            </h2>
            {grouped[priority].map((suggestion) => (
              <SuggestionCard key={suggestion.id} suggestion={suggestion} />
            ))}
          </div>
        );
      })}
    </div>
  );
}

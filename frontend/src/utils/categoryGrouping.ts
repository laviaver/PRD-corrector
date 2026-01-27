/**
 * Category grouping utilities for suggestions.
 */

import { Suggestion } from '../services/analysisService';

export interface GroupedSuggestions {
  [category: string]: Suggestion[];
}

/**
 * Group suggestions by category.
 */
export function groupByCategory(suggestions: Suggestion[]): GroupedSuggestions {
  return suggestions.reduce((acc, suggestion) => {
    const category = suggestion.category;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(suggestion);
    return acc;
  }, {} as GroupedSuggestions);
}

/**
 * Group suggestions by priority.
 */
export function groupByPriority(suggestions: Suggestion[]): GroupedSuggestions {
  return suggestions.reduce((acc, suggestion) => {
    const priority = suggestion.priority;
    if (!acc[priority]) {
      acc[priority] = [];
    }
    acc[priority].push(suggestion);
    return acc;
  }, {} as GroupedSuggestions);
}

/**
 * Get category display label.
 */
export function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    structure: 'Structure & Organization',
    clarity: 'Clarity',
    completeness: 'Completeness',
    best_practices: 'Best Practices',
    technical_quality: 'Technical Quality',
  };
  return labels[category] || category;
}

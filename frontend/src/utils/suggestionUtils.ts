/**
 * Utilities for filtering and sorting suggestions.
 */

import { Suggestion } from '../services/analysisService';

export type SortOption = 'priority' | 'category' | 'title';
export type FilterOption = {
  category?: string;
  priority?: 'high' | 'medium' | 'low';
};

/**
 * Sort suggestions by the specified option.
 */
export function sortSuggestions(
  suggestions: Suggestion[],
  sortBy: SortOption = 'priority'
): Suggestion[] {
  const sorted = [...suggestions];

  switch (sortBy) {
    case 'priority':
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return sorted.sort(
        (a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]
      );

    case 'category':
      return sorted.sort((a, b) => a.category.localeCompare(b.category));

    case 'title':
      return sorted.sort((a, b) => a.title.localeCompare(b.title));

    default:
      return sorted;
  }
}

/**
 * Filter suggestions by category and/or priority.
 */
export function filterSuggestions(
  suggestions: Suggestion[],
  filter: FilterOption
): Suggestion[] {
  return suggestions.filter((suggestion) => {
    if (filter.category && suggestion.category !== filter.category) {
      return false;
    }
    if (filter.priority && suggestion.priority !== filter.priority) {
      return false;
    }
    return true;
  });
}

/**
 * Get unique categories from suggestions.
 */
export function getCategories(suggestions: Suggestion[]): string[] {
  const categories = new Set(suggestions.map((s) => s.category));
  return Array.from(categories).sort();
}

/**
 * Get unique priorities from suggestions.
 */
export function getPriorities(suggestions: Suggestion[]): ('high' | 'medium' | 'low')[] {
  const priorities = new Set(suggestions.map((s) => s.priority));
  return Array.from(priorities).sort((a, b) => {
    const order = { high: 0, medium: 1, low: 2 };
    return order[a] - order[b];
  });
}

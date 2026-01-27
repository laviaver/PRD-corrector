/**
 * LocalStorage utilities for PRD Reviewer frontend.
 *
 * Handles saving and loading PRD content and editor state.
 */

const PRD_EDITOR_KEY = 'prd_editor_content';
const PRD_HISTORY_KEY = 'prd_history';

/**
 * Save PRD content to localStorage.
 */
export function savePRDContent(content: string): void {
  try {
    localStorage.setItem(PRD_EDITOR_KEY, content);
  } catch (err) {
    console.error('Failed to save PRD content:', err);
  }
}

/**
 * Load PRD content from localStorage.
 */
export function loadPRDContent(): string | null {
  try {
    return localStorage.getItem(PRD_EDITOR_KEY);
  } catch (err) {
    console.error('Failed to load PRD content:', err);
    return null;
  }
}

/**
 * Clear saved PRD content.
 */
export function clearPRDContent(): void {
  try {
    localStorage.removeItem(PRD_EDITOR_KEY);
  } catch (err) {
    console.error('Failed to clear PRD content:', err);
  }
}

/**
 * Save PRD to history.
 */
export function saveToHistory(prdId: string, content: string, timestamp: string): void {
  try {
    const history = getHistory();
    history.unshift({ prdId, content, timestamp });
    // Keep only last 10 entries
    const limited = history.slice(0, 10);
    localStorage.setItem(PRD_HISTORY_KEY, JSON.stringify(limited));
  } catch (err) {
    console.error('Failed to save to history:', err);
  }
}

/**
 * Get PRD history.
 */
export function getHistory(): Array<{ prdId: string; content: string; timestamp: string }> {
  try {
    const history = localStorage.getItem(PRD_HISTORY_KEY);
    return history ? JSON.parse(history) : [];
  } catch (err) {
    console.error('Failed to load history:', err);
    return [];
  }
}

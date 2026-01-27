/**
 * Clipboard utilities for copying text to clipboard.
 */

/**
 * Copy text to clipboard.
 */
export async function copyToClipboard(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
    } catch (fallbackErr) {
      throw new Error('Failed to copy to clipboard');
    } finally {
      document.body.removeChild(textArea);
    }
  }
}

/**
 * Check if clipboard API is available.
 */
export function isClipboardAvailable(): boolean {
  return !!navigator.clipboard && !!navigator.clipboard.writeText;
}

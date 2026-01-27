/**
 * Comparison utilities for PRD comparison mode.
 */

export interface Section {
  title: string;
  content: string;
}

/**
 * Extract sections from PRD content.
 */
export function extractSections(content: string): Section[] {
  const sections: Section[] = [];
  const lines = content.split('\n');
  let currentSection: Section | null = null;

  for (const line of lines) {
    const headerMatch = line.match(/^(#+)\s+(.+)$/);
    if (headerMatch) {
      if (currentSection) {
        sections.push(currentSection);
      }
      currentSection = {
        title: headerMatch[2],
        content: line + '\n',
      };
    } else if (currentSection) {
      currentSection.content += line + '\n';
    }
  }

  if (currentSection) {
    sections.push(currentSection);
  }

  return sections;
}

/**
 * Compare two PRDs and find missing sections.
 */
export function findMissingSections(
  userPRD: string,
  templatePRD: string
): { missing: string[]; extra: string[] } {
  const userSections = extractSections(userPRD);
  const templateSections = extractSections(templatePRD);

  const userTitles = userSections.map((s) => s.title.toLowerCase().trim());
  const templateTitles = templateSections.map((s) => s.title.toLowerCase().trim());

  const missing = templateTitles.filter(
    (title) => !userTitles.some((ut) => ut.includes(title) || title.includes(ut))
  );

  const extra = userTitles.filter(
    (title) => !templateTitles.some((tt) => tt.includes(title) || title.includes(tt))
  );

  return {
    missing: missing.map((title) => {
      const section = templateSections.find((s) => s.title.toLowerCase().trim() === title);
      return section?.title || title;
    }),
    extra: extra.map((title) => {
      const section = userSections.find((s) => s.title.toLowerCase().trim() === title);
      return section?.title || title;
    }),
  };
}

/**
 * Normalize section title for comparison.
 */
export function normalizeTitle(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .trim();
}

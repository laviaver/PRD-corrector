import { useState } from 'react';
import './ComparisonView.css';

interface ComparisonViewProps {
  userPRD: string;
  templatePRD: string;
  templateName: string;
}

export default function ComparisonView({
  userPRD,
  templatePRD,
  templateName,
}: ComparisonViewProps) {
  const [viewMode, setViewMode] = useState<'side-by-side' | 'diff'>('side-by-side');

  // Simple section extraction (in production, use more sophisticated parsing)
  const extractSections = (content: string): string[] => {
    const sections: string[] = [];
    const lines = content.split('\n');
    let currentSection = '';

    for (const line of lines) {
      if (line.match(/^#+\s/)) {
        if (currentSection) {
          sections.push(currentSection.trim());
        }
        currentSection = line + '\n';
      } else {
        currentSection += line + '\n';
      }
    }
    if (currentSection) {
      sections.push(currentSection.trim());
    }
    return sections;
  };

  const userSections = extractSections(userPRD);
  const templateSections = extractSections(templatePRD);

  const userSectionTitles = userSections.map((s) => s.split('\n')[0].replace(/^#+\s/, ''));
  const templateSectionTitles = templateSections.map((s) => s.split('\n')[0].replace(/^#+\s/, ''));

  const missingSections = templateSectionTitles.filter(
    (title) => !userSectionTitles.some((ut) => ut.toLowerCase().includes(title.toLowerCase()))
  );

  return (
    <div className="comparison-view">
      <div className="comparison-header">
        <h2>PRD Comparison: Your PRD vs {templateName}</h2>
        <div className="view-mode-toggle">
          <button
            className={viewMode === 'side-by-side' ? 'active' : ''}
            onClick={() => setViewMode('side-by-side')}
          >
            Side by Side
          </button>
          <button
            className={viewMode === 'diff' ? 'active' : ''}
            onClick={() => setViewMode('diff')}
          >
            Differences
          </button>
        </div>
      </div>

      {viewMode === 'side-by-side' ? (
        <div className="side-by-side-view">
          <div className="comparison-panel">
            <h3>Your PRD</h3>
            <div className="prd-content">
              <pre>{userPRD}</pre>
            </div>
          </div>
          <div className="comparison-panel">
            <h3>Template: {templateName}</h3>
            <div className="prd-content">
              <pre>{templatePRD}</pre>
            </div>
          </div>
        </div>
      ) : (
        <div className="diff-view">
          <div className="missing-sections">
            <h3>Missing Sections</h3>
            {missingSections.length > 0 ? (
              <ul>
                {missingSections.map((section, idx) => (
                  <li key={idx}>{section}</li>
                ))}
              </ul>
            ) : (
              <p>All template sections are present in your PRD!</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

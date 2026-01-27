import { useState } from 'react';
import './BestPracticesLibrary.css';

interface Practice {
  id: string;
  category: string;
  title: string;
  description: string;
  example: string;
  template?: string;
}

const practices: Practice[] = [
  {
    id: '1',
    category: 'Structure',
    title: 'Executive Summary',
    description: 'Every PRD should start with an executive summary that provides a high-level overview.',
    example: 'Executive Summary: This PRD describes a new feature that will...',
    template: '## Executive Summary\n\n[Brief overview of the product/feature]\n\n[Key goals and objectives]',
  },
  {
    id: '2',
    category: 'Structure',
    title: 'User Stories Format',
    description: 'User stories should follow the "As a... I want... So that..." format.',
    example: 'As a user, I want to upload files, so that I can share documents.',
    template: '**As a** [user type]\n**I want** [action]\n**So that** [benefit]',
  },
  {
    id: '3',
    category: 'Completeness',
    title: 'Success Metrics',
    description: 'Define measurable success criteria for the product.',
    example: 'Success Metrics: 80% user satisfaction, 50% reduction in processing time.',
    template: '## Success Metrics\n\n- [Metric 1]: [Target]\n- [Metric 2]: [Target]',
  },
  {
    id: '4',
    category: 'Clarity',
    title: 'Clear Problem Statement',
    description: 'Clearly articulate the problem being solved.',
    example: 'Problem: Users currently spend 2 hours manually reviewing documents.',
    template: '## Problem Statement\n\n[Clear description of the problem]\n\n[Why this problem matters]',
  },
];

export default function BestPracticesLibrary() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedPractice, setSelectedPractice] = useState<Practice | null>(null);

  const categories = ['all', ...Array.from(new Set(practices.map((p) => p.category)))];

  const filteredPractices =
    selectedCategory === 'all'
      ? practices
      : practices.filter((p) => p.category === selectedCategory);

  return (
    <div className="best-practices-library">
      <h2>PRD Best Practices Library</h2>

      <div className="library-content">
        <div className="practices-sidebar">
          <div className="category-filter">
            <label>Filter by Category:</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'All Categories' : cat}
                </option>
              ))}
            </select>
          </div>

          <div className="practices-list">
            {filteredPractices.map((practice) => (
              <div
                key={practice.id}
                className={`practice-item ${selectedPractice?.id === practice.id ? 'selected' : ''}`}
                onClick={() => setSelectedPractice(practice)}
              >
                <h4>{practice.title}</h4>
                <p className="practice-category">{practice.category}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="practice-detail">
          {selectedPractice ? (
            <>
              <h3>{selectedPractice.title}</h3>
              <p className="practice-description">{selectedPractice.description}</p>

              {selectedPractice.example && (
                <div className="practice-example">
                  <strong>Example:</strong>
                  <pre>{selectedPractice.example}</pre>
                </div>
              )}

              {selectedPractice.template && (
                <div className="practice-template">
                  <strong>Template:</strong>
                  <pre>{selectedPractice.template}</pre>
                  <button
                    className="btn-copy-template"
                    onClick={() => navigator.clipboard.writeText(selectedPractice.template!)}
                  >
                    Copy Template
                  </button>
                </div>
              )}
            </>
          ) : (
            <p>Select a practice to view details</p>
          )}
        </div>
      </div>
    </div>
  );
}

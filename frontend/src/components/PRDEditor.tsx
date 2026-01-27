import { useState, useEffect } from 'react';
import './PRDEditor.css';

interface PRDEditorProps {
  initialContent: string;
  onContentChange?: (content: string) => void;
  onSave?: (content: string) => void;
}

export default function PRDEditor({
  initialContent,
  onContentChange,
  onSave,
}: PRDEditorProps) {
  const [content, setContent] = useState(initialContent);
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    setContent(initialContent);
    setIsDirty(false);
  }, [initialContent]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    setIsDirty(true);
    onContentChange?.(newContent);
  };

  const handleSave = () => {
    // Save to localStorage
    localStorage.setItem('prd_editor_content', content);
    setIsDirty(false);
    onSave?.(content);
  };

  // Auto-save debounced
  useEffect(() => {
    if (!isDirty) return;

    const timer = setTimeout(() => {
      localStorage.setItem('prd_editor_content', content);
      setIsDirty(false);
    }, 2000); // 2 second debounce

    return () => clearTimeout(timer);
  }, [content, isDirty]);

  return (
    <div className="prd-editor">
      <div className="editor-header">
        <h3>PRD Editor</h3>
        <div className="editor-actions">
          {isDirty && <span className="unsaved-indicator">Unsaved changes</span>}
          <button onClick={handleSave} className="btn-save" disabled={!isDirty}>
            Save
          </button>
        </div>
      </div>
      <textarea
        value={content}
        onChange={handleChange}
        className="editor-textarea"
        placeholder="Edit your PRD content here..."
      />
      <div className="editor-footer">
        <span className="char-count">{content.length} characters</span>
      </div>
    </div>
  );
}

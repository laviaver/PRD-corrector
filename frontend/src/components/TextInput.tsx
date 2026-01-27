import { useState } from 'react';
import './TextInput.css';

interface TextInputProps {
  onTextSubmit: (text: string) => void;
  onError?: (error: string) => void;
  placeholder?: string;
}

export default function TextInput({
  onTextSubmit,
  onError,
  placeholder = 'Paste your PRD content here...',
}: TextInputProps) {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!text.trim()) {
      onError?.('Please enter some content.');
      return;
    }

    onTextSubmit(text.trim());
  };

  const handleClear = () => {
    setText('');
  };

  return (
    <div className="text-input">
      <form onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          className="text-area"
          rows={10}
        />
        <div className="text-input-actions">
          <button type="button" onClick={handleClear} className="btn-clear">
            Clear
          </button>
          <button type="submit" className="btn-submit">
            Submit PRD
          </button>
        </div>
      </form>
    </div>
  );
}

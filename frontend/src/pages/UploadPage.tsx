import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import TextInput from '../components/TextInput';
import ContentPreview from '../components/ContentPreview';
import ErrorModal from '../components/ErrorModal';
import { uploadPRDFile, pastePRDText, getMarkdownPreview } from '../services/prdService';
import { formatError, logError } from '../utils/errorHandler';
import './UploadPage.css';

export default function UploadPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewContent, setPreviewContent] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [showInvalidFileModal, setShowInvalidFileModal] = useState(false);
  const [invalidFileName, setInvalidFileName] = useState<string>('');
  const [showMarkdownModal, setShowMarkdownModal] = useState(false);
  const [markdownContent, setMarkdownContent] = useState<string>('');
  const [markdownLoading, setMarkdownLoading] = useState(false);
  const [markdownError, setMarkdownError] = useState<string>('');

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError('');

    // Read file for preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setPreviewContent(content);
    };
    reader.onerror = () => {
      setError('Failed to read file for preview.');
    };

    const name = file.name.toLowerCase();
    if (
      file.type === 'text/plain' ||
      name.endsWith('.txt') ||
      name.endsWith('.md')
    ) {
      reader.readAsText(file);
    } else if (name.endsWith('.docx')) {
      setPreviewContent(`File: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);
    } else {
      setPreviewContent(`File: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreviewContent('');
    setError('');
    setShowMarkdownModal(false);
    setMarkdownError('');
  };

  const handleViewMarkdown = async () => {
    if (!selectedFile) return;
    setMarkdownError('');
    const name = selectedFile.name.toLowerCase();
    if (name.endsWith('.txt') || name.endsWith('.md')) {
      setMarkdownContent(previewContent);
      setShowMarkdownModal(true);
      return;
    }
    if (name.endsWith('.docx')) {
      setMarkdownLoading(true);
      try {
        const result = await getMarkdownPreview(selectedFile);
        setMarkdownContent(result.markdown);
        setShowMarkdownModal(true);
      } catch (err) {
        setMarkdownError(formatError(err));
        logError(err, 'UploadPage.handleViewMarkdown');
      } finally {
        setMarkdownLoading(false);
      }
    } else {
      setMarkdownContent(previewContent);
      setShowMarkdownModal(true);
    }
  };

  const handleInvalidFileType = (filename: string) => {
    setInvalidFileName(filename);
    setShowInvalidFileModal(true);
    setSelectedFile(null);
    setPreviewContent('');
  };

  const handleTextSubmit = async (text: string) => {
    setError('');
    setLoading(true);

    try {
      const response = await pastePRDText(text);
      // Navigate with analysis_id, not prd_id
      if (response.analysis_id) {
        navigate(`/analysis/${response.analysis_id}`);
      } else {
        setError('Analysis ID not returned from server');
      }
    } catch (err) {
      const errorMessage = formatError(err);
      setError(errorMessage);
      logError(err, 'UploadPage.handleTextSubmit');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await uploadPRDFile(selectedFile);
      // Navigate with analysis_id, not prd_id
      if (response.analysis_id) {
        navigate(`/analysis/${response.analysis_id}`);
      } else {
        setError('Analysis ID not returned from server');
      }
    } catch (err) {
      const errorMessage = formatError(err);
      setError(errorMessage);
      logError(err, 'UploadPage.handleFileUpload');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <h1>Upload PRD for Review</h1>
      <p className="page-description">
        Upload a PRD file or paste your PRD content to get AI-powered suggestions for improvement.
      </p>

      <div className="upload-options">
        <div className="upload-option">
          <h2>Upload File</h2>
          <FileUpload
            onFileSelect={handleFileSelect}
            onError={setError}
            onInvalidFileType={handleInvalidFileType}
          />
          {selectedFile && (
            <div className="file-selected">
              <div className="file-selected-row">
                <p>Selected: {selectedFile.name}</p>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  disabled={loading}
                  className="btn-remove"
                  title="Remove file"
                >
                  Remove
                </button>
              </div>
              <div className="file-selected-actions">
                <button
                  type="button"
                  onClick={handleViewMarkdown}
                  disabled={loading || markdownLoading}
                  className="btn-view-markdown"
                  title="View markdown version"
                >
                  {markdownLoading ? 'Loading…' : 'View Markdown'}
                </button>
                <button
                  onClick={handleFileUpload}
                  disabled={loading}
                  className="btn-upload"
                >
                  {loading ? 'Uploading...' : 'Upload & Analyze'}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="divider">OR</div>

        <div className="upload-option">
          <h2>Paste Text</h2>
          <TextInput
            onTextSubmit={handleTextSubmit}
            onError={setError}
          />
        </div>
      </div>

      {previewContent && selectedFile && (
        <ContentPreview
          content={previewContent}
          filename={selectedFile.name}
        />
      )}

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <ErrorModal
        isOpen={showInvalidFileModal}
        title="Invalid File Type"
        message={`The file "${invalidFileName}" is not supported. Please upload only .docx, .md, or .txt files.`}
        onAcknowledge={() => {
          setShowInvalidFileModal(false);
          setInvalidFileName('');
        }}
      />

      {showMarkdownModal && (
        <div className="markdown-modal-overlay" onClick={() => setShowMarkdownModal(false)}>
          <div className="markdown-modal" onClick={(e) => e.stopPropagation()}>
            <div className="markdown-modal-header">
              <h3>Markdown</h3>
              <button
                type="button"
                className="markdown-modal-close"
                onClick={() => setShowMarkdownModal(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            {markdownError ? (
              <div className="markdown-modal-error">{markdownError}</div>
            ) : (
              <pre className="markdown-modal-content">{markdownContent}</pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

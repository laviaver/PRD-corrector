import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import TextInput from '../components/TextInput';
import ContentPreview from '../components/ContentPreview';
import ErrorModal from '../components/ErrorModal';
import { uploadPRDFile, pastePRDText } from '../services/prdService';
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
              <p>Selected: {selectedFile.name}</p>
              <button
                onClick={handleFileUpload}
                disabled={loading}
                className="btn-upload"
              >
                {loading ? 'Uploading...' : 'Upload & Analyze'}
              </button>
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
    </div>
  );
}

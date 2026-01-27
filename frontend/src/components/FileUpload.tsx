import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onError?: (error: string) => void;
  acceptedTypes?: string[];
  maxSize?: number;
}

export default function FileUpload({
  onFileSelect,
  onError,
  acceptedTypes = ['.txt', '.md', '.docx'],
  maxSize = 10 * 1024 * 1024, // 10MB
}: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors) {
          const error = rejection.errors[0];
          if (error.code === 'file-too-large') {
            onError?.('File is too large. Maximum size is 10MB.');
          } else if (error.code === 'file-invalid-type') {
            onError?.('Invalid file type. Please upload .txt, .md, or .docx files.');
          } else {
            onError?.(error.message || 'File upload failed.');
          }
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect, onError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize,
    multiple: false,
  });

  return (
    <div className="file-upload">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          {isDragActive ? (
            <p>Drop the file here...</p>
          ) : (
            <>
              <p>Drag & drop a PRD file here, or click to select</p>
              <p className="file-types">Supported: {acceptedTypes.join(', ')}</p>
              <p className="file-size">Max size: 10MB</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

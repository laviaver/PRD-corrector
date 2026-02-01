import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onError?: (error: string) => void;
  onInvalidFileType?: (filename: string) => void;
  acceptedTypes?: string[];
  maxSize?: number;
}

// Only accept .docx, .md, .txt
const ALLOWED_FILE_TYPES = {
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/markdown': ['.md'],
  'text/plain': ['.txt'],
};

const ALLOWED_EXTENSIONS = ['.docx', '.md', '.txt'];

const DEFAULT_ACCEPTED_TYPES = ALLOWED_EXTENSIONS;

export default function FileUpload({
  onFileSelect,
  onError,
  onInvalidFileType,
  acceptedTypes = DEFAULT_ACCEPTED_TYPES,
  maxSize = 10 * 1024 * 1024, // 10MB
}: FileUploadProps) {
  const validateFileType = (file: File): boolean => {
    const fileName = file.name.toLowerCase();
    const extension = fileName.substring(fileName.lastIndexOf('.'));
    return ALLOWED_EXTENSIONS.includes(extension);
  };

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // First check rejected files from dropzone
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors) {
          const error = rejection.errors[0];
          if (error.code === 'file-too-large') {
            onError?.('File is too large. Maximum size is 10MB.');
          } else if (error.code === 'file-invalid-type') {
            const fileName = rejection.file?.name || 'Unknown file';
            onInvalidFileType?.(fileName);
          } else {
            onError?.(error.message || 'File upload failed.');
          }
        }
        return;
      }

      // Additional validation for accepted files
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        if (!validateFileType(file)) {
          onInvalidFileType?.(file.name);
          return;
        }
        onFileSelect(file);
      }
    },
    [onFileSelect, onError, onInvalidFileType]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ALLOWED_FILE_TYPES,
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
              <p className="file-types">
                Accepted file types: <strong>.docx</strong>, <strong>.md</strong>, <strong>.txt</strong>
              </p>
              <p className="file-size">Max size: 10MB</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

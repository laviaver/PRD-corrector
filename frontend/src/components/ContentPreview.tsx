import './ContentPreview.css';

interface ContentPreviewProps {
  content: string;
  maxLength?: number;
  filename?: string;
}

export default function ContentPreview({
  content,
  maxLength = 500,
  filename,
}: ContentPreviewProps) {
  const preview = content.length > maxLength
    ? `${content.substring(0, maxLength)}...`
    : content;

  const isTruncated = content.length > maxLength;

  return (
    <div className="content-preview">
      {filename && (
        <div className="preview-header">
          <span className="filename">{filename}</span>
          <span className="file-size">
            {content.length.toLocaleString()} characters
          </span>
        </div>
      )}
      <div className="preview-content">
        <pre>{preview}</pre>
      </div>
      {isTruncated && (
        <div className="preview-footer">
          <span className="truncated-message">
            Preview truncated. Full content: {content.length.toLocaleString()} characters
          </span>
        </div>
      )}
    </div>
  );
}

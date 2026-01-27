import './PRDViewer.css';

interface PRDViewerProps {
  content: string;
  filename?: string;
}

export default function PRDViewer({ content, filename }: PRDViewerProps) {
  return (
    <div className="prd-viewer">
      {filename && (
        <div className="viewer-header">
          <h3>{filename}</h3>
        </div>
      )}
      <div className="viewer-content">
        <pre>{content}</pre>
      </div>
    </div>
  );
}

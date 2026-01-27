import './LoadingSkeleton.css';

interface LoadingSkeletonProps {
  type?: 'text' | 'card' | 'list';
  lines?: number;
}

export default function LoadingSkeleton({ type = 'text', lines = 3 }: LoadingSkeletonProps) {
  if (type === 'card') {
    return (
      <div className="skeleton-card">
        <div className="skeleton-line skeleton-title" />
        <div className="skeleton-line skeleton-content" />
        <div className="skeleton-line skeleton-content short" />
      </div>
    );
  }

  if (type === 'list') {
    return (
      <div className="skeleton-list">
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="skeleton-line" />
        ))}
      </div>
    );
  }

  return (
    <div className="skeleton-text">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton-line" />
      ))}
    </div>
  );
}

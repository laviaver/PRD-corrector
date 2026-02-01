import './ErrorModal.css';

interface ErrorModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  onAcknowledge: () => void;
}

export default function ErrorModal({
  isOpen,
  title,
  message,
  onAcknowledge,
}: ErrorModalProps) {
  if (!isOpen) return null;

  return (
    <div className="error-modal-overlay" onClick={onAcknowledge}>
      <div className="error-modal-content" onClick={(e) => e.stopPropagation()}>
        <h2 className="error-modal-title">{title}</h2>
        <p className="error-modal-message">{message}</p>
        <button className="error-modal-button" onClick={onAcknowledge}>
          Acknowledge
        </button>
      </div>
    </div>
  );
}

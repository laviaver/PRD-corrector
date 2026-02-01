import './ScoreGauge.css';

interface ScoreGaugeProps {
  label: string;
  score: number;
  max?: number;
}

function scoreColor(score: number, max: number): string {
  const pct = max ? (score / max) * 100 : 0;
  if (pct >= 67) return '#28a745';
  if (pct >= 34) return '#ffc107';
  return '#dc3545';
}

const SEMICIRCLE_LENGTH = Math.PI * 40; // radius 40

export default function ScoreGauge({ label, score, max = 100 }: ScoreGaugeProps) {
  const value = Math.min(max, Math.max(0, score));
  const pct = max ? (value / max) * 100 : 0;
  const color = scoreColor(value, max);
  const dashLength = (pct / 100) * SEMICIRCLE_LENGTH;

  return (
    <div className="score-gauge">
      <div className="score-gauge-svg" aria-hidden>
        <svg viewBox="0 0 100 55" className="gauge-svg">
          <path
            className="gauge-track"
            d="M 10 50 A 40 40 0 0 1 90 50"
            fill="none"
            strokeWidth="8"
          />
          <path
            className="gauge-fill"
            d="M 10 50 A 40 40 0 0 1 90 50"
            fill="none"
            strokeWidth="8"
            stroke={color}
            strokeDasharray={`${dashLength} ${SEMICIRCLE_LENGTH}`}
            strokeLinecap="round"
          />
        </svg>
      </div>
      <div className="score-gauge-value" style={{ color }}>
        {value}/{max}
      </div>
      <div className="score-gauge-label">{label}</div>
    </div>
  );
}

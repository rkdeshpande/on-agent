import React, { useState } from 'react';

interface Recommendation {
  recommendation: string;
  rationale: string;
  impact: string;
  confidence_level: string;
  risk_level: string;
}

interface Props {
  strategy: {
    conservative: Recommendation[];
    moderate: Recommendation[];
    aggressive: Recommendation[];
  };
}

const StrategyTabs: React.FC<Props> = ({ strategy }) => {
  const [selected, setSelected] = useState<'conservative' | 'moderate' | 'aggressive'>('moderate');

  const levels = ['conservative', 'moderate', 'aggressive'] as const;
  const colors: Record<typeof levels[number], string> = {
    conservative: '#28a745', // green
    moderate: '#ffc107',     // yellow
    aggressive: '#dc3545'    // red
  };

  const activeColor = colors[selected];

  return (
    <section style={{ marginBottom: '2rem' }}>
      <h2>🧭 Strategy Options</h2>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        {levels.map((level) => (
          <button
            key={level}
            onClick={() => setSelected(level)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              border: `2px solid ${colors[level]}`,
              backgroundColor: selected === level ? colors[level] : 'white',
              color: selected === level ? 'white' : colors[level],
              fontWeight: selected === level ? 'bold' : 'normal',
              cursor: 'pointer'
            }}
          >
            {level.charAt(0).toUpperCase() + level.slice(1)}
          </button>
        ))}
      </div>

      {strategy[selected].map((item, idx) => (
        <div key={idx} style={{
          border: `1px solid ${activeColor}`,
          borderLeft: `4px solid ${activeColor}`,
          padding: '1rem',
          marginBottom: '1rem',
          backgroundColor: '#f9f9f9'
        }}>
          <h4 style={{ marginBottom: '0.5rem' }}>{item.recommendation}</h4>
          <p style={{ margin: '0.25rem 0' }}><strong>Rationale:</strong> {item.rationale}</p>
          <p style={{ margin: '0.25rem 0' }}><strong>Impact:</strong> {item.impact}</p>
          <p style={{ margin: '0.25rem 0' }}>
            <strong>Confidence:</strong> {item.confidence_level} | <strong>Risk:</strong> {item.risk_level}
          </p>
        </div>
      ))}
    </section>
  );
};

export default StrategyTabs;

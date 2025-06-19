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

  const getButtonClasses = (level: typeof levels[number]) => {
    const baseClasses = "px-4 py-2 rounded-full border-2 text-sm font-medium capitalize transition-colors";
    
    if (selected === level) {
      switch (level) {
        case 'conservative': return `${baseClasses} bg-green-600 text-white border-green-600`;
        case 'moderate': return `${baseClasses} bg-yellow-600 text-white border-yellow-600`;
        case 'aggressive': return `${baseClasses} bg-red-600 text-white border-red-600`;
      }
    } else {
      switch (level) {
        case 'conservative': return `${baseClasses} text-green-600 border-green-600 hover:bg-green-100`;
        case 'moderate': return `${baseClasses} text-yellow-600 border-yellow-600 hover:bg-yellow-100`;
        case 'aggressive': return `${baseClasses} text-red-600 border-red-600 hover:bg-red-100`;
      }
    }
  };

  const getCardClasses = (level: typeof levels[number]) => {
    const baseClasses = "border-l-4 bg-white p-4 rounded shadow-sm";
    switch (level) {
      case 'conservative': return `${baseClasses} border-green-600`;
      case 'moderate': return `${baseClasses} border-yellow-600`;
      case 'aggressive': return `${baseClasses} border-red-600`;
    }
  };

  return (
    <section className="mb-10">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">🧭 Strategy Options</h2>

      <div className="flex gap-2 mb-6">
        {levels.map((level) => (
          <button
            key={level}
            onClick={() => setSelected(level)}
            className={getButtonClasses(level)}
          >
            {level}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {strategy[selected].map((item, idx) => (
          <div
            key={idx}
            className={getCardClasses(selected)}
          >
            <h4 className="font-semibold mb-1">{item.recommendation}</h4>
            <p className="text-sm text-gray-700 mb-1"><strong>Rationale:</strong> {item.rationale}</p>
            <p className="text-sm text-gray-700 mb-1"><strong>Impact:</strong> {item.impact}</p>
            <p className="text-sm text-gray-700">
              <strong>Confidence:</strong> {item.confidence_level} | <strong>Risk:</strong> {item.risk_level}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default StrategyTabs;

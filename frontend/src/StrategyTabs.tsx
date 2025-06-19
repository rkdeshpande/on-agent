import React, { useState } from 'react';
import DecisionFactorsAndImpacts from './DecisionFactorsAndImpacts';

interface Recommendation {
  recommendation: string;
  rationale: string;
  impact: string;
  confidence_level: string;
  risk_level: string;
}

interface Rationale {
  conservative_rationale: string;
  moderate_rationale: string;
  aggressive_rationale: string;
  decision_factors: string[];
  client_history_impact: string;
  comparable_deals_impact: string;
  risk_profile_considerations: string;
}

interface Props {
  strategy: {
    conservative: Recommendation[];
    moderate: Recommendation[];
    aggressive: Recommendation[];
  };
  rationale?: Rationale;
}

const StrategyTabs: React.FC<Props> = ({ strategy, rationale }) => {
  const [selected, setSelected] = useState<'conservative' | 'moderate' | 'aggressive'>('moderate');
  const [showRationale, setShowRationale] = useState(false);
  
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

  const getTopLevelRationale = (level: typeof levels[number]) => {
    if (!rationale) return '';
    switch (level) {
      case 'conservative': return rationale.conservative_rationale;
      case 'moderate': return rationale.moderate_rationale;
      case 'aggressive': return rationale.aggressive_rationale;
    }
  };  

  return (
    <section className="mb-10">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">🧭 Strategy Options</h2>

      <div className="bg-white border rounded-lg shadow-sm p-5 transition-all">

        {/* Strategy Tabs */}
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

        {/* Strategy Recommendations */}
        <div className="space-y-4">
          {strategy[selected].map((item, idx) => (
            <div
              key={idx}
              className={getCardClasses(selected)}
            >
              <h4 className="font-semibold mb-1">{item.recommendation}</h4>
              <p className="text-sm text-gray-700 mb-1">
                <strong>Rationale:</strong> {item.rationale}
              </p>
              <p className="text-sm text-gray-700 mb-1">
                <strong>Impact:</strong> {item.impact}
              </p>
              <p className="text-sm text-gray-700">
                <strong>Confidence:</strong> {item.confidence_level} | <strong>Risk:</strong> {item.risk_level}
              </p>
            </div>
          ))}
        </div>

        {/* Expandable Top-Level Rationale */}
        {rationale && (
          <div className="mt-6 border-t pt-4">
            <button
              className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
              onClick={() => setShowRationale(!showRationale)}
            >
              <svg
                className={`w-4 h-4 transition-transform duration-300 ${showRationale ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
              {showRationale ? 'Hide' : 'Show'} Top-Level Rationale
            </button>

            {showRationale && (
              <div className="mt-3 text-sm text-gray-700 leading-relaxed">
                {getTopLevelRationale(selected)}
              </div>
            )}
          </div>
        )}

      </div>
      {rationale && (
        <DecisionFactorsAndImpacts rationale={rationale} />
      )}
    </section>
  );
};

export default StrategyTabs;

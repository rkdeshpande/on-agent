import React from 'react';

interface Props {
  rationale: {
    decision_factors: string[];
    client_history_impact: string;
    comparable_deals_impact: string;
    risk_profile_considerations: string;
  };
}

const DecisionFactorsAndImpacts: React.FC<Props> = ({ rationale }) => {
  return (
    <section className="mt-10 bg-gray-50 border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">📌 Decision Drivers</h3>

      <div className="flex flex-wrap gap-2 mb-6">
        {rationale.decision_factors.map((factor, idx) => (
          <span
            key={idx}
            className="px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-medium"
          >
            {factor}
          </span>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-700">
        <div>
          <h4 className="font-medium text-gray-600 mb-1">Client History Impact</h4>
          <p>{rationale.client_history_impact}</p>
        </div>

        <div>
          <h4 className="font-medium text-gray-600 mb-1">Comparable Deals Impact</h4>
          <p>{rationale.comparable_deals_impact}</p>
        </div>

        <div className="md:col-span-2">
          <h4 className="font-medium text-gray-600 mb-1">Risk Profile Considerations</h4>
          <p>{rationale.risk_profile_considerations}</p>
        </div>
      </div>
    </section>
  );
};

export default DecisionFactorsAndImpacts;

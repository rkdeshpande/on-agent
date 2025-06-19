import React from 'react';

interface Props {
  gaps: any[];
}

const InformationGaps: React.FC<Props> = ({ gaps }) => {
  return (
    <div className="space-y-4 text-sm text-gray-800">
      {gaps.map((gap, i) => (
        <div
          key={i}
          className="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded shadow-sm"
        >
          <p className="font-semibold mb-1">❗ {gap.gap_description}</p>
          <p><strong>Recommended Action:</strong> {gap.recommended_action}</p>
          <p><strong>Impact:</strong> {gap.impact_on_strategy}</p>
        </div>
      ))}
    </div>
  );
};

export default InformationGaps;

import React from 'react';

interface Props {
  gaps: any[];
}

const InformationGaps: React.FC<Props> = ({ gaps }) => {
  return (
    <section>
      <h2>🚨 Information Gaps</h2>
      {gaps.map((gap, i) => (
        <div key={i} style={{ backgroundColor: '#fff3cd', padding: '1rem', marginBottom: '1rem' }}>
          <strong>{gap.gap_description}</strong>
          <p><strong>Recommended Action:</strong> {gap.recommended_action}</p>
          <p><strong>Impact:</strong> {gap.impact_on_strategy}</p>
        </div>
      ))}
    </section>
  );
};

export default InformationGaps;

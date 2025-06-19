import React, { useState } from 'react';
import ContextSummary from './ContextSummary';
import DomainKnowledge from './DomainKnowledge';
import InformationGaps from './InformationGaps';
import DebugPanel from './DebugPanel';

interface Props {
  data: any;
}

const TabbedPanel: React.FC<Props> = ({ data }) => {
  const tabs = ['Context', 'Knowledge', 'Gaps', 'Debug'] as const;
  const [activeTab, setActiveTab] = useState<typeof tabs[number]>('Context');

  return (
    <div style={{ marginTop: '2rem' }}>
      <div style={{
        display: 'flex',
        gap: '1rem',
        borderBottom: '2px solid #ccc',
        marginBottom: '1rem'
      }}>
        {tabs.map((tab) => (
          <div
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '0.5rem 1rem',
              cursor: 'pointer',
              borderBottom: activeTab === tab ? '3px solid #007bff' : '3px solid transparent',
              fontWeight: activeTab === tab ? 'bold' : 'normal',
            }}
          >
            {tab}
          </div>
        ))}
      </div>

      <div style={{ padding: '1rem', border: '1px solid #ddd' }}>
        {activeTab === 'Context' && <ContextSummary context={data.context_summary} />}
        {activeTab === 'Knowledge' && <DomainKnowledge items={data.relevant_domain_knowledge} />}
        {activeTab === 'Gaps' && <InformationGaps gaps={data.information_gaps} />}
        {activeTab === 'Debug' && <DebugPanel data={data} />}
      </div>
    </div>
  );
};

export default TabbedPanel;

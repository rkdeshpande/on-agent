import React, { useState } from 'react';
import ContextSummary from './ContextSummary';
import DomainKnowledge from './DomainKnowledge';
import InformationGaps from './InformationGaps';

interface Props {
  data: any;
}

const TabbedPanel: React.FC<Props> = ({ data }) => {
  const tabs = ['Deal Context', 'Domain Knowledge', 'Information Gaps'] as const;
  const [activeTab, setActiveTab] = useState<typeof tabs[number]>('Deal Context');

  const tabStyles = (tab: string) =>
    `px-6 py-3 text-base font-medium border-b-2 transition ${
      activeTab === tab
        ? 'border-blue-600 text-blue-600'
        : 'border-transparent text-gray-500 hover:text-blue-500 hover:border-blue-300'
    }`;

  // Debug logging
  console.log('TabbedPanel data:', data);
  console.log('Context summary:', data?.context_summary);
  console.log('Domain knowledge:', data?.relevant_domain_knowledge);
  console.log('Information gaps:', data?.information_gaps);
  console.log('Rationale:', data?.rationale);

  return (
    <section className="mt-8">
      <div className="flex gap-6 border-b border-gray-200 mb-4">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={tabStyles(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-md p-6 shadow-sm text-sm">
        {activeTab === 'Deal Context' && data?.context_summary && <ContextSummary context={data.context_summary} />}
        {activeTab === 'Deal Context' && !data?.context_summary && <div className="text-gray-500">No context summary available</div>}
        
        {activeTab === 'Domain Knowledge' && data?.relevant_domain_knowledge && <DomainKnowledge items={data.relevant_domain_knowledge} />}
        {activeTab === 'Domain Knowledge' && !data?.relevant_domain_knowledge && <div className="text-gray-500">No domain knowledge available</div>}
        
        {activeTab === 'Information Gaps' && data?.information_gaps && <InformationGaps gaps={data.information_gaps} />}
        {activeTab === 'Information Gaps' && !data?.information_gaps && <div className="text-gray-500">No information gaps available</div>}
      </div>
    </section>
  );
};

export default TabbedPanel;

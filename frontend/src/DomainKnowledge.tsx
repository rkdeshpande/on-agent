import React from 'react';

interface Props {
  items: any[];
}

const DomainKnowledge: React.FC<Props> = ({ items }) => {
  return (
    <div className="space-y-4 text-sm text-gray-800">
      {items.map((entry, i) => (
        <div key={i} className="bg-white p-4 border rounded shadow-sm">
          <h4 className="font-semibold text-blue-700 mb-2">
            📚 {entry.chunk?.text?.split('\n')[0] || 'Knowledge Chunk'}
          </h4>
          <p className="mb-1"><strong>Relevance:</strong> {entry.relevance_reason}</p>
          <p><strong>Application:</strong> {entry.application_context}</p>
        </div>
      ))}
    </div>
  );
};

export default DomainKnowledge;

import React from 'react';

interface Props {
  items: any[];
}

const DomainKnowledge: React.FC<Props> = ({ items }) => {
  return (
    <section>
      <h2>📚 Relevant Domain Knowledge</h2>
      {items.map((entry, i) => (
        <div key={i} style={{ borderBottom: '1px solid #ccc', paddingBottom: '1rem', marginBottom: '1rem' }}>
          <pre>{entry.chunk.text}</pre>
          <p><strong>Relevance:</strong> {entry.relevance_reason}</p>
          <p><strong>Application:</strong> {entry.application_context}</p>
        </div>
      ))}
    </section>
  );
};

export default DomainKnowledge;

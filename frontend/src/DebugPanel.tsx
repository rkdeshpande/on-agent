import React, { useState } from 'react';

interface Props {
  data: any;
}

const DebugPanel: React.FC<Props> = ({ data }) => {
  const [expanded, setExpanded] = useState(false);

  if (!data) return null;

  const toggle = () => setExpanded(!expanded);

  return (
    <section style={{ marginTop: '2rem' }}>
      <button onClick={toggle} style={{ marginBottom: '1rem' }}>
        {expanded ? '🔽 Hide Debug Output' : '🔼 Show Debug Output'}
      </button>

      {expanded && (
        <div
          style={{
            backgroundColor: '#f6f8fa',
            border: '1px solid #ccc',
            padding: '1rem',
            maxHeight: '500px',
            overflowY: 'scroll',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
          }}
        >
          <h3>Reasoning Steps</h3>
          <pre>{JSON.stringify(data.reasoning_steps || [], null, 2)}</pre>

          <h3>Used Domain Chunks</h3>
          <pre>{JSON.stringify(data.used_domain_chunks || [], null, 2)}</pre>

          <h3>Decision Basis</h3>
          <pre>{JSON.stringify(data.decision_basis || [], null, 2)}</pre>
        </div>
      )}
    </section>
  );
};

export default DebugPanel;

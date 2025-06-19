import React, { useState } from 'react';

interface Props {
  data: any;
}

const DebugPanel: React.FC<Props> = ({ data }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-sm text-blue-600 hover:underline"
      >
        {expanded ? 'Hide Debug Output' : 'Show Debug Output'}
      </button>

      {expanded && (
        <div className="mt-2 bg-gray-100 p-4 rounded overflow-auto max-h-[400px] text-xs text-gray-700">
          <h4 className="font-semibold mb-1">Reasoning Steps</h4>
          <pre className="mb-2">{JSON.stringify(data.reasoning_steps, null, 2)}</pre>

          <h4 className="font-semibold mb-1">Used Domain Chunks</h4>
          <pre className="mb-2">{JSON.stringify(data.used_domain_chunks, null, 2)}</pre>

          <h4 className="font-semibold mb-1">Decision Basis</h4>
          <pre>{JSON.stringify(data.decision_basis, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default DebugPanel;

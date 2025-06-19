import { useState } from 'react';
import StrategyTabs from './StrategyTabs';
import TabbedPanel from './TabbedPanel';

function App() {
  const [dealId, setDealId] = useState('');
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const runAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const formData = new URLSearchParams();
    formData.append('deal_id', dealId);

    try {
      const res = await fetch('/run', {
        method: 'POST',
        body: formData,
      });

      const json = await res.json();
      // Extract the actual result data from the Flask response wrapper
      const result = json.result || json;
      setData(result);
    } catch (err) {
      console.error("Agent error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{
      fontFamily: 'sans-serif',
      padding: '2rem',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      backgroundColor: '#f8f9fb',
      minHeight: '100vh'
    }}>
      <div style={{
        maxWidth: '700px',
        width: '100%',
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        textAlign: 'center',
        marginBottom: '2rem'
      }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', color: '#1a2e42' }}>
          Agentic Deal Assistant
        </h1>
        <p style={{ fontSize: '1rem', marginBottom: '1.5rem', color: '#5c6b7c' }}>
          Analyze, recommend, and negotiate smarter with AI-driven insights.
        </p>

        <form onSubmit={runAgent} style={{
          display: 'flex',
          gap: '0.5rem',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <input
            value={dealId}
            onChange={(e) => setDealId(e.target.value)}
            placeholder="Enter Deal ID (e.g., DEAL123)"
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              width: '60%',
              minWidth: '250px'
            }}
          />
          <button type="submit" disabled={loading} style={{
            padding: '0.5rem 1rem',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}>
            {loading ? 'Running...' : 'Run'}
          </button>
        </form>

        {loading && (
          <div style={{ marginTop: '1rem', width: '100%', height: '6px', backgroundColor: '#eee' }}>
            <div style={{
              width: '100%',
              height: '100%',
              backgroundColor: '#007bff',
              animation: 'progress 1.5s infinite'
            }} />
            <style>
              {`
                @keyframes progress {
                  0% { transform: translateX(-100%); }
                  50% { transform: translateX(0); }
                  100% { transform: translateX(100%); }
                }
                div[style*="animation: progress"] {
                  transition: transform 0.2s;
                }
              `}
            </style>
          </div>
        )}
      </div>

      {data && (
        <div style={{ width: '100%', maxWidth: '900px' }}>
          <StrategyTabs strategy={data.strategy} />
          <TabbedPanel data={data} />
        </div>
      )}
    </main>
  );
}

export default App;

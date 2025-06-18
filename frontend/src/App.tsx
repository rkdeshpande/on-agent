import { useState } from 'react';

function App() {
  const [dealId, setDealId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new URLSearchParams();
    formData.append('deal_id', dealId);

    try {
      const res = await fetch('/run', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError('Failed to run agent. Check backend logs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '600px', margin: 'auto' }}>
      <h1>Agentic Deal Assistant</h1>
      <form onSubmit={handleSubmit}>
        <input
          value={dealId}
          onChange={(e) => setDealId(e.target.value)}
          placeholder="Enter Deal ID (e.g., DEAL123)"
          required
          style={{ padding: '0.5rem', width: '100%', marginBottom: '1rem' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '0.5rem 1rem' }}>
          {loading ? 'Running...' : 'Run Agent'}
        </button>
      </form>
      {error && <div style={{ color: 'red', marginTop: '1rem' }}>{error}</div>}
      {result && (
        <pre style={{ backgroundColor: '#f5f5f5', padding: '1rem', marginTop: '1rem' }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </main>
  );
}

export default App;

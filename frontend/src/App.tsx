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
      const result = json.result || json;
      setData(result);
    } catch (err) {
      console.error("Agent error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen w-full bg-gray-50 font-sans text-gray-800">
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="bg-white p-8 rounded shadow-md text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Agentic Offer & Negotiation Cockpit</h1>
          <p className="text-gray-500 mb-6">
            Analyze, recommend, and negotiate smarter with AI-driven insights.
          </p>

          <form onSubmit={runAgent} className="flex flex-wrap justify-center gap-4 mb-4">
            <input
              value={dealId}
              onChange={(e) => setDealId(e.target.value)}
              placeholder="Enter Deal ID (e.g., DEAL123)"
              className="border border-gray-300 px-4 py-2 rounded w-64"
            />
            <button
              type="submit"
              disabled={loading}
              className={`px-4 py-2 rounded text-white ${loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? 'Running...' : 'Run'}
            </button>
          </form>

          {loading && (
            <div className="w-full bg-gray-200 h-2 rounded overflow-hidden">
              <div className="bg-blue-600 h-full animate-pulse w-full" />
            </div>
          )}
        </div>

        {data?.strategy && (
          <div className="space-y-10">
            <StrategyTabs strategy={data.strategy} />
            <TabbedPanel data={data} />
          </div>
        )}
      </div>
    </main>
  );
}

export default App;

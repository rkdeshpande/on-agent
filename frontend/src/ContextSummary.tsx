import React from 'react';

interface Props {
  context: any;
}

const ContextSummary: React.FC<Props> = ({ context }) => {
  const { deal_summary, client_summary, negotiation_context, comparable_deals } = context;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm text-gray-800">
      <div className="bg-white p-4 border rounded shadow-sm">
        <h3 className="font-semibold mb-2">📄 Deal Summary</h3>
        <ul className="space-y-1">
          <li><strong>Coverage:</strong> {deal_summary.coverage_terms}</li>
          <li><strong>Risk:</strong> {deal_summary.risk_profile}</li>
          <li><strong>Premium:</strong> {deal_summary.premium_structure}</li>
          <li><strong>LOB:</strong> {deal_summary.line_of_business}</li>
          <li><strong>Territory:</strong> {deal_summary.territory}</li>
          <li><strong>Offer:</strong> {deal_summary.current_offer_details}</li>
        </ul>
        <p className="mt-2 font-medium">⚠️ Key Risk Factors:</p>
        <ul className="list-disc list-inside">
          {deal_summary.key_risk_factors.map((f: string, i: number) => (
            <li key={i}>{f}</li>
          ))}
        </ul>
      </div>

      <div className="bg-white p-4 border rounded shadow-sm">
        <h3 className="font-semibold mb-2">👤 Client Summary</h3>
        <ul className="space-y-1">
          <li><strong>Relationship:</strong> {client_summary.relationship_duration}</li>
          <li><strong>Claims:</strong> {client_summary.claim_history}</li>
          <li><strong>Payments:</strong> {client_summary.payment_history}</li>
          <li><strong>Style:</strong> {client_summary.negotiation_style}</li>
        </ul>
        <p className="mt-2 font-medium">📎 Prior Negotiations:</p>
        <ul className="list-disc list-inside">
          {client_summary.prior_negotiation_history.map((h: string, i: number) => (
            <li key={i}>{h}</li>
          ))}
        </ul>
      </div>

      <div className="bg-white p-4 border rounded shadow-sm">
        <h3 className="font-semibold mb-2">💬 Negotiation Context</h3>
        <p className="font-medium">Client Objections:</p>
        <ul className="list-disc list-inside mb-2">
          {negotiation_context.current_objections.map((o: string, i: number) => (
            <li key={i}>{o}</li>
          ))}
        </ul>
        <p className="font-medium">Discussion Progress:</p>
        <ul className="list-disc list-inside mb-2">
          {negotiation_context.discussion_progress.map((p: string, i: number) => (
            <li key={i}>{p}</li>
          ))}
        </ul>
        <p className="font-medium">Offer History:</p>
        <ul className="list-disc list-inside mb-2">
          {negotiation_context.offer_history.map((h: string, i: number) => (
            <li key={i}>{h}</li>
          ))}
        </ul>
        <p className="font-medium">Client Priorities:</p>
        <ul className="list-disc list-inside">
          {negotiation_context.client_priorities.map((p: string, i: number) => (
            <li key={i}>{p}</li>
          ))}
        </ul>
      </div>

      <div className="md:col-span-2 lg:col-span-3 bg-white p-4 border rounded shadow-sm">
        <h3 className="font-semibold mb-2">📈 Comparable Deals</h3>
        <p><strong>Market Trends:</strong> {comparable_deals.market_trends}</p>
        <p><strong>Benchmarks:</strong> {comparable_deals.benchmark_insights}</p>
        {comparable_deals.similar_deals.map((deal: any, i: number) => (
          <div key={i} className="mt-2 border-t pt-2">
            <p><strong>{deal.reference_deal_id}</strong> — <em>{deal.similarity_reason}</em></p>
            <p className="text-sm italic">{deal.outcome_summary}</p>
            <ul className="list-disc list-inside">
              {deal.key_learnings.map((l: string, j: number) => (
                <li key={j}>📌 {l}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContextSummary;

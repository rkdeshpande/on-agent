import React from 'react';

interface Props {
  context: any;
}

const ContextSummary: React.FC<Props> = ({ context }) => {
  const { deal_summary, client_summary, negotiation_context, comparable_deals } = context;

  return (
    <section style={{ marginTop: '2rem' }}>
      <h2>📘 Context Summary</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ flex: '1', minWidth: '300px', padding: '1rem', border: '1px solid #ccc' }}>
          <h3>📄 Deal Summary</h3>
          <ul>
            <li><strong>Coverage Terms:</strong> {deal_summary.coverage_terms}</li>
            <li><strong>Risk Profile:</strong> {deal_summary.risk_profile}</li>
            <li><strong>Premium Structure:</strong> {deal_summary.premium_structure}</li>
            <li><strong>Line of Business:</strong> {deal_summary.line_of_business}</li>
            <li><strong>Territory:</strong> {deal_summary.territory}</li>
            <li><strong>Offer:</strong> {deal_summary.current_offer_details}</li>
          </ul>
          <p><strong>Key Risk Factors:</strong></p>
          <ul>
            {deal_summary.key_risk_factors.map((factor: string, i: number) => (
              <li key={i}>⚠️ {factor}</li>
            ))}
          </ul>
        </div>

        <div style={{ flex: '1', minWidth: '300px', padding: '1rem', border: '1px solid #ccc' }}>
          <h3>👤 Client Summary</h3>
          <ul>
            <li><strong>Relationship:</strong> {client_summary.relationship_duration}</li>
            <li><strong>Claims:</strong> {client_summary.claim_history}</li>
            <li><strong>Payments:</strong> {client_summary.payment_history}</li>
            <li><strong>Style:</strong> {client_summary.negotiation_style}</li>
          </ul>
          <p><strong>Prior Negotiation:</strong></p>
          <ul>
            {client_summary.prior_negotiation_history.map((h: string, i: number) => (
              <li key={i}>📎 {h}</li>
            ))}
          </ul>
        </div>

        <div style={{ flex: '1', minWidth: '300px', padding: '1rem', border: '1px solid #ccc' }}>
          <h3>💬 Negotiation Context</h3>
          <p><strong>Objections:</strong></p>
          <ul>
            {negotiation_context.current_objections.map((o: string, i: number) => (
              <li key={i}>❗ {o}</li>
            ))}
          </ul>
          <p><strong>Progress:</strong></p>
          <ul>
            {negotiation_context.discussion_progress.map((p: string, i: number) => (
              <li key={i}>📍 {p}</li>
            ))}
          </ul>
          <p><strong>Offer History:</strong></p>
          <ul>
            {negotiation_context.offer_history.map((o: string, i: number) => (
              <li key={i}>📊 {o}</li>
            ))}
          </ul>
          <p><strong>Client Priorities:</strong></p>
          <ul>
            {negotiation_context.client_priorities.map((p: string, i: number) => (
              <li key={i}>🎯 {p}</li>
            ))}
          </ul>
        </div>
      </div>

      <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc' }}>
        <h3>📈 Comparable Deals</h3>
        <p><strong>Market Trends:</strong> {comparable_deals.market_trends}</p>
        <p><strong>Benchmark Insights:</strong> {comparable_deals.benchmark_insights}</p>
        {comparable_deals.similar_deals.map((deal: any, i: number) => (
          <div key={i} style={{ marginTop: '1rem' }}>
            <p><strong>{deal.reference_deal_id}</strong> – {deal.similarity_reason}</p>
            <p><em>{deal.outcome_summary}</em></p>
            <ul>
              {deal.key_learnings.map((l: string, j: number) => (
                <li key={j}>📌 {l}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ContextSummary;

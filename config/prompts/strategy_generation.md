You are an expert insurance negotiator. Your task is to generate a negotiation strategy based on the deal context, domain knowledge, and identified decision rules.

Deal Context:
{deal_context}

Domain Knowledge:
{domain_knowledge}

Decision Rules Applied:
{decision_rules}

Generate a detailed negotiation strategy that:
1. Addresses the client's objections
2. Leverages the client's history
3. Uses insights from comparable deals
4. Considers the risk profile
5. Provides specific recommendations for premium and deductible adjustments
6. Handles coverage requests appropriately

Your strategy should explicitly incorporate the decision rules that were triggered. For example:
- If a premium objection rule was triggered, explain how you're using deductible adjustments
- If a coverage request rule was triggered, explain how you're addressing the coverage needs
- If a high-risk rule was triggered, explain how you're adjusting coverage for risk mitigation

For coverage requests:
- Evaluate if the request is reasonable given the risk profile
- Consider if additional coverage can be offered within existing limits
- Suggest alternative coverage options if direct request cannot be accommodated
- Explain any coverage limitations or exclusions clearly

Format your response as a structured strategy with clear sections.

================ FEW-SHOT EXAMPLES ================

=== EXAMPLE 1: PREMIUM OBJECTION SCENARIO ===

Deal Context Summary:
- Deal ID: EXAMPLE123
- Line of Business: Commercial Property
- Risk Profile: Medium-risk retail facility
- Current Terms: $8M limit, $75K deductible
- Premium: $180K annually (Quarterly payments)

Key Objections:
1. Premium too high compared to market rates
2. Concern about quarterly payment structure

Domain Rules Used:
1. Premium Objection → Deductible Trade
   - Justification: Client has history of accepting deductible adjustments
   - Confidence: High - Matches objection pattern and client history

2. Payment Structure → Flexible Terms
   - Justification: Client has good payment history
   - Confidence: High - Based on relationship notes

Strategy:
1. Premium Adjustment
   - Current: $180K annually
   - Proposed: $170K annually
   - Justification:
     * Client's good payment history
     * No major claims
     * Comparable deal benchmark (DEAL456)

2. Deductible Trade-off
   - Current: $75K
   - Proposed: $90K
   - Justification:
     * Offsets premium reduction
     * Maintains risk coverage
     * Aligns with client's deductible acceptance history

3. Payment Structure
   - Current: Quarterly payments
   - Proposed: Monthly payments with 2% discount for annual payment
   - Justification:
     * Provides flexibility
     * Rewards annual commitment
     * Based on client's payment history

Rationale:
1. Premium Reduction
   - Supported by client's clean claims history
   - Validated by comparable deal (DEAL456)
   - Within acceptable risk parameters

2. Deductible Increase
   - Balanced trade-off for premium reduction
   - Client has demonstrated acceptance of similar adjustments
   - Maintains appropriate risk coverage

3. Payment Flexibility
   - Addresses cash flow concerns
   - Rewards long-term commitment
   - Based on client's payment history

Expected Outcome:
- Premium reduction addresses market comparison concern
- Deductible adjustment maintains risk coverage
- Flexible payment options improve client satisfaction
- Strategy leverages client history and comparable deals

=== END EXAMPLE 1 ===

=== EXAMPLE 2: COVERAGE REQUEST SCENARIO ===
Deal Context Summary:
- Deal ID: COVREQ001
- Line of Business: Commercial Property
- Risk Profile: Low-risk office park
- Current Terms: $12M limit, $100K deductible
- Premium: $200K annually

Key Objections:
1. Request for flood coverage
2. Request for higher business interruption limit

Domain Rules Used:
1. Coverage Request → Evaluate Against Limits
   - Justification: Client requested additional coverage types
   - Confidence: High - Explicit coverage request

2. Coverage Cap → Exclusion/Alternative
   - Justification: Requested coverage exceeds domain limits
   - Confidence: High - Based on policy guidelines

Strategy:
1. Flood Coverage
   - Current: Not included
   - Proposed: Offer sublimit of $1M for flood, subject to underwriting
   - Justification:
     * Flood risk is moderate in this territory
     * Comparable deal (COVDEAL002) included $1M flood sublimit

2. Business Interruption Limit
   - Current: $2M
   - Proposed: $2.5M (max allowed by guidelines)
   - Justification:
     * Requested $3M exceeds domain cap
     * $2.5M is the highest available for this risk profile
     * Explain cap and rationale to client

Rationale:
- Flood coverage is offered within prudent risk management
- Business interruption limit is maximized per guidelines
- Transparent communication about exclusions and caps

Expected Outcome:
- Client receives additional coverage within risk and policy limits
- Clear rationale for any exclusions or caps
- Strategy leverages comparable deals and domain knowledge

=== END EXAMPLE 2 ===

=== EXAMPLE 3: HIGH-RISK SCENARIO ===
Deal Context Summary:
- Deal ID: HIGHRISK01
- Line of Business: Manufacturing
- Risk Profile: High-risk chemical plant
- Current Terms: $20M limit, $500K deductible
- Premium: $1.2M annually

Key Objections:
1. Premium is too high
2. Deductible is too high

Domain Rules Used:
1. High Risk → Enhanced Coverage/Strict Terms
   - Justification: High-risk profile requires stricter terms
   - Confidence: Medium - Based on risk assessment

2. Premium Objection → Deductible Trade (limited)
   - Justification: Some flexibility, but must maintain risk controls
   - Confidence: Low - Limited by risk profile

Strategy:
1. Premium Adjustment
   - Current: $1.2M
   - Proposed: $1.15M (minimum for this risk)
   - Justification:
     * High-risk profile limits premium reduction
     * Comparable deal (HRDEAL03) had $1.18M premium

2. Deductible Adjustment
   - Current: $500K
   - Proposed: $450K (minimum allowed)
   - Justification:
     * Some flexibility for client
     * Must maintain risk controls
     * Explain rationale and limits

3. Enhanced Safety Requirements
   - Proposed: Require additional safety audits and compliance
   - Justification:
     * Mitigates risk for both parties
     * May allow for future premium/deductible improvements

Rationale:
- High-risk profile constrains flexibility
- Adjustments are made within strict risk and policy limits
- Safety improvements are required for future concessions

Expected Outcome:
- Client receives modest premium/deductible relief
- Safety requirements are clearly communicated
- Strategy is justified by risk profile, comparable deals, and domain knowledge

=== END EXAMPLE 3 ===

================ END FEW-SHOT EXAMPLES ================

Now, please generate a negotiation strategy for the current deal context following this structured format. 
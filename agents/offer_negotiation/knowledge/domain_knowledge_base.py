"""Domain knowledge base for the offer negotiation agent."""

from typing import Any, Dict, List

from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk


class DomainKnowledgeBase:
    """Base class for domain knowledge retrieval."""

    def __init__(self):
        """Initialize the knowledge base with sample data."""
        self._knowledge_chunks = [
            DocumentChunk(
                chunk_id="sample_1",
                text="Premium objections can be addressed by adjusting deductibles or payment terms.",
                source_doc_id="sample_doc",
                metadata={"document_type": "negotiation_strategy"},
            ),
            DocumentChunk(
                chunk_id="sample_2",
                text="Manufacturing facilities typically require higher coverage limits.",
                source_doc_id="sample_doc",
                metadata={"document_type": "risk_guidelines"},
            ),
            DocumentChunk(
                chunk_id="sample_3",
                text="Quarterly payments are preferred for premium amounts over $100K.",
                source_doc_id="sample_doc",
                metadata={"document_type": "payment_guidelines"},
            ),
            DocumentChunk(
                chunk_id="sample_4",
                text="Deductible adjustments should be proportional to premium changes.",
                source_doc_id="sample_doc",
                metadata={"document_type": "negotiation_strategy"},
            ),
            DocumentChunk(
                chunk_id="sample_5",
                text="Medium-risk facilities should maintain minimum $100K deductible.",
                source_doc_id="sample_doc",
                metadata={"document_type": "risk_guidelines"},
            ),
        ]

    def add_document_chunks(self, chunks: list) -> None:
        """Add document chunks to the knowledge base."""
        for chunk in chunks:
            if isinstance(chunk, DocumentChunk):
                self._knowledge_chunks.append(chunk)
            elif isinstance(chunk, dict):
                self._knowledge_chunks.append(DocumentChunk(**chunk))
            else:
                # Try to coerce to dict then DocumentChunk
                self._knowledge_chunks.append(DocumentChunk(**dict(chunk)))

    def retrieve(self, information_need: str) -> List[DocumentChunk]:
        """Retrieve relevant domain knowledge chunks for a given information need.

        Args:
            information_need: The information need to retrieve knowledge for

        Returns:
            List of relevant DocumentChunk objects
        """
        # Simple keyword-based matching for now
        # In a real implementation, this would use semantic search
        relevant_chunks = []

        # Map information needs to keywords
        need_keywords = {
            "submission.risk_profile": ["risk", "facility", "guidelines"],
            "submission.premium_structure": ["premium", "payment", "terms"],
            "submission.deductible": ["deductible", "adjustment"],
            "submission.coverage_terms": ["coverage", "limit"],
            "client_history.prior_negotiations": ["negotiation", "strategy"],
        }

        # Get keywords for this need
        keywords = need_keywords.get(information_need, [])

        # Find relevant chunks
        for chunk in self._knowledge_chunks:
            if any(keyword in chunk.text.lower() for keyword in keywords):
                relevant_chunks.append(chunk)

        return relevant_chunks

    def get_chunks_by_type(self, doc_type: str) -> List[DocumentChunk]:
        """Return all knowledge chunks matching the given document type."""
        doc_type_str = str(doc_type)
        return [
            chunk
            for chunk in self._knowledge_chunks
            if str(chunk.metadata.get("document_type")) == doc_type_str
        ]

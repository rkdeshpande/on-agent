from typing import Dict, List

from .domain_documents import DocumentChunk, DocumentType


class DomainKnowledgeBase:
    """Repository for storing and retrieving domain knowledge chunks."""

    def __init__(self):
        # Store chunks by their ID for quick lookup
        self._chunks: Dict[str, DocumentChunk] = {}
        # Index chunks by document type for faster filtering
        self._chunks_by_type: Dict[DocumentType, List[str]] = {
            doc_type: [] for doc_type in DocumentType
        }

    def add_document_chunks(self, chunks: List[DocumentChunk]) -> None:
        """
        Add a list of document chunks to the knowledge base.

        Args:
            chunks: List of DocumentChunk objects to add
        """
        for chunk in chunks:
            # Store the chunk
            self._chunks[chunk.chunk_id] = chunk

            # Index by document type
            doc_type = chunk.metadata.get("document_type")
            if doc_type in self._chunks_by_type:
                self._chunks_by_type[doc_type].append(chunk.chunk_id)

    def get_chunks_by_type(self, doc_type: DocumentType) -> List[DocumentChunk]:
        """
        Retrieve all chunks of a specific document type.

        Args:
            doc_type: The type of document to retrieve

        Returns:
            List of DocumentChunk objects of the specified type
        """
        chunk_ids = self._chunks_by_type.get(doc_type, [])
        return [self._chunks[chunk_id] for chunk_id in chunk_ids]

    def search_chunks(self, query: str) -> List[DocumentChunk]:
        """
        Search for chunks containing the query string.
        Basic case-insensitive keyword matching for now.

        Args:
            query: The search query string

        Returns:
            List of DocumentChunk objects containing the query
        """
        query = query.lower()
        return [chunk for chunk in self._chunks.values() if query in chunk.text.lower()]

    def get_all_chunks(self) -> List[DocumentChunk]:
        """Get all chunks in the knowledge base."""
        return list(self._chunks.values())

    def clear(self) -> None:
        """Clear all chunks from the knowledge base."""
        self._chunks.clear()
        self._chunks_by_type = {doc_type: [] for doc_type in DocumentType}


# Example usage
if __name__ == "__main__":
    from domain_documents import DocumentProcessor, DocumentType, DomainDocument

    # Create a knowledge base
    kb = DomainKnowledgeBase()

    # Create and process a sample document
    sample_doc = DomainDocument(
        doc_id="DOC001",
        type=DocumentType.NEGOTIATION_FRAMEWORK,
        source_name="Commercial Property Negotiation Guide",
        content="""
        High-Risk Property Negotiation Strategy
        
        When dealing with high-risk properties, always begin by understanding the client's risk mitigation measures.
        
        Key points to address:
        1. Current safety protocols
        2. Recent improvements
        3. Future risk reduction plans
        
        Premium Structure Considerations
        
        Consider offering tiered premium structures based on risk mitigation implementation.
        """,
    )

    # Process and add chunks
    processor = DocumentProcessor()
    chunks = processor.parse(sample_doc)
    kb.add_document_chunks(chunks)

    # Test retrieval by type
    print("\nChunks by type (NEGOTIATION_FRAMEWORK):")
    framework_chunks = kb.get_chunks_by_type(DocumentType.NEGOTIATION_FRAMEWORK)
    for chunk in framework_chunks:
        print(f"\nChunk {chunk.chunk_id}:")
        print(f"Text: {chunk.text[:100]}...")

    # Test search
    print("\nSearch results for 'premium':")
    search_results = kb.search_chunks("premium")
    for chunk in search_results:
        print(f"\nChunk {chunk.chunk_id}:")
        print(f"Text: {chunk.text[:100]}...")

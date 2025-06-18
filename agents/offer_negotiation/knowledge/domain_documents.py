import re
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from config.app_config import config


class DocumentType(str, Enum):
    """Types of domain knowledge documents."""

    NEGOTIATION_FRAMEWORK = "negotiation_framework"
    UNDERWRITING_GUIDELINE = "underwriting_guideline"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    BEST_PRACTICES = "best_practices"


class DomainDocument(BaseModel):
    """Represents a domain knowledge document."""

    doc_id: str
    type: DocumentType
    source_name: str
    content: str


class DocumentChunk(BaseModel):
    """Represents a semantic chunk extracted from a document."""

    chunk_id: str
    text: str
    source_doc_id: str
    metadata: Dict = Field(default_factory=dict)


class DocumentProcessor:
    """Base class for processing domain documents into semantic chunks."""

    def __init__(self):
        # Simple paragraph splitting regex
        self.paragraph_splitter = re.compile(r"\n\s*\n")

    def parse(self, document: DomainDocument) -> List[DocumentChunk]:
        """
        Parse a domain document into semantic chunks.

        Args:
            document: The domain document to parse

        Returns:
            List of document chunks with metadata
        """
        # Split into paragraphs
        paragraphs = self.paragraph_splitter.split(document.content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        for i, para in enumerate(paragraphs):
            chunk = DocumentChunk(
                chunk_id=f"{document.doc_id}_chunk_{i}",
                text=para,
                source_doc_id=document.doc_id,
                metadata={
                    "document_type": document.type,
                    "source_name": document.source_name,
                    "paragraph_index": i,
                },
            )
            chunks.append(chunk)

        return chunks


def load_domain_documents(
    base_path: Optional[str] = None,
) -> List[DomainDocument]:
    """
    Load domain documents from the specified directory.

    Args:
        base_path: Path to the directory containing domain knowledge documents.
                   If None, uses the configured domain knowledge directory.

    Returns:
        List of loaded DomainDocument objects
    """
    documents = []
    base_dir = Path(base_path) if base_path else config.domain_knowledge_dir

    # Map file names to document types
    type_mapping = {
        "coverage_limits.md": DocumentType.UNDERWRITING_GUIDELINE,
        "negotiation_framework.md": DocumentType.NEGOTIATION_FRAMEWORK,
        "regulatory_requirements.md": DocumentType.REGULATORY_REQUIREMENT,
        "best_practices.md": DocumentType.BEST_PRACTICES,
    }

    # Load each document
    for file_path in base_dir.glob("*.md"):
        doc_type = type_mapping.get(file_path.name, DocumentType.BEST_PRACTICES)
        with open(file_path, "r") as f:
            content = f.read()
            doc = DomainDocument(
                doc_id=file_path.stem,
                type=doc_type,
                source_name=file_path.name,
                content=content,
            )
            documents.append(doc)

    return documents


# Example usage
if __name__ == "__main__":
    # Create a sample document
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

    # Process the document
    processor = DocumentProcessor()
    chunks = processor.parse(sample_doc)

    # Print results
    print("Document chunks:")
    for chunk in chunks:
        print(f"\nChunk {chunk.chunk_id}:")
        print(f"Text: {chunk.text[:100]}...")
        print(f"Metadata: {chunk.metadata}")

import logging
from pathlib import Path
from typing import Optional, Union

from .document_processor import extract_text_from_document, is_supported_document

logger = logging.getLogger(__name__)


def is_text_file(file_path: Path) -> bool:
    """
    Determine if a file is text-based by attempting to read it as text.

    Args:
        file_path: Path to the file to check

    Returns:
        bool: True if the file can be read as text, False otherwise
    """
    try:
        # Try to read the first few bytes as text
        with open(file_path, "r", encoding="utf-8") as f:
            f.read(1024)
        return True
    except UnicodeDecodeError:
        return False
    except Exception as e:
        logger.debug(f"Error checking file {file_path}: {str(e)}")
        return False


def load_submission_context(
    submission_id: str, submission_dir: Optional[Union[str, Path]] = None
) -> dict[str, str]:
    """
    Load all text-based files and supported documents from a submission directory.

    Args:
        submission_id: The ID of the submission to load
        submission_dir: Optional custom path to the submission directory.
                       If not provided, defaults to "data/submissions/{submission_id}"

    Returns:
        Dictionary mapping filenames to their contents
    """
    # Construct the submission directory path
    if submission_dir is None:
        submission_dir = Path("data/submissions") / submission_id
    else:
        submission_dir = Path(submission_dir)

    # Check if directory exists
    if not submission_dir.exists():
        logger.warning(f"Submission directory not found: {submission_dir}")
        return {}

    # Get all files and sort them
    files = sorted(
        [
            f
            for f in submission_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
    )

    if not files:
        logger.warning(f"No files found in {submission_dir}")
        return {}

    # Load each file's contents
    file_contents = {}
    for file_path in files:
        try:
            # Handle document files
            if is_supported_document(file_path):
                content = extract_text_from_document(file_path)
                if content:
                    file_contents[file_path.name] = content.strip()
                    logger.debug(f"Loaded document: {file_path.name}")
                continue

            # Handle text files
            if is_text_file(file_path):
                content = file_path.read_text(encoding="utf-8")
                if content.strip():  # Only include non-empty files
                    file_contents[file_path.name] = content.strip()
                    logger.debug(f"Loaded text file: {file_path.name}")
            else:
                logger.debug(f"Skipping binary file: {file_path.name}")

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            continue

    # Validate we have at least one file
    if not file_contents:
        logger.warning(f"No readable files found in {submission_dir}")

    return file_contents

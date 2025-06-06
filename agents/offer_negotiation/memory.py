import logging
from pathlib import Path

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


def load_submission_context(submission_id: str) -> dict[str, str]:
    """
    Load all text-based files from a submission directory.

    Args:
        submission_id: The ID of the submission to load

    Returns:
        Dictionary mapping filenames to their contents
    """
    # Construct the submission directory path
    submission_dir = Path("data/submissions") / submission_id

    # Check if directory exists
    if not submission_dir.exists():
        logger.warning(f"Submission directory not found: {submission_dir}")
        return {}

    # Get all text files and sort them
    text_files = sorted(
        [
            f
            for f in submission_dir.iterdir()
            if f.is_file() and not f.name.startswith(".") and is_text_file(f)
        ]
    )

    if not text_files:
        logger.warning(f"No text files found in {submission_dir}")
        return {}

    # Load each file's contents
    file_contents = {}
    for file_path in text_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            if content.strip():  # Only include non-empty files
                file_contents[file_path.name] = content.strip()
                logger.debug(f"Loaded file: {file_path.name}")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            continue

    # Validate we have at least one file
    if not file_contents:
        logger.warning(f"No readable files found in {submission_dir}")

    return file_contents

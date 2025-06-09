import logging

logger = logging.getLogger(__name__)


def get_past_rationale(deal_id: str) -> str:
    """
    Get past rationale for a deal.

    Args:
        deal_id: The ID of the deal

    Returns:
        Past rationale as a string, or empty string if none found
    """
    logger.info(f"Fetching past rationale for deal_id: {deal_id}")
    # TODO: Implement actual rationale fetching
    return ""

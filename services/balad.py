import aiohttp, logging

logger = logging.getLogger(__name__)

async def search_balad(city: str, category: str, max_results: int = 200) -> list:
    """
    Balad.ir is blocked on non-Iranian servers.
    This stub returns empty list gracefully.
    """
    logger.info('Balad: skipped (blocked on non-IR servers)')
    return []

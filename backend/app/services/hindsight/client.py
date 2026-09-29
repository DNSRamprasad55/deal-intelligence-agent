from typing import Optional
from hindsight_client import Hindsight
from app.core.config import settings
from app.core.logging import logger

_hindsight_client_instance: Optional[Hindsight] = None


def get_hindsight_client() -> Optional[Hindsight]:
    global _hindsight_client_instance
    api_key = settings.HINDSIGHT_API_KEY
    base_url = settings.get_hindsight_base_url()

    if not api_key or not api_key.strip():
        return None

    if _hindsight_client_instance is None:
        logger.info(f"Initializing official Hindsight Cloud client (Base URL: {base_url})")
        _hindsight_client_instance = Hindsight(
            base_url=base_url,
            api_key=api_key,
            timeout=30.0
        )
    return _hindsight_client_instance


def reset_hindsight_client_instance():
    global _hindsight_client_instance
    _hindsight_client_instance = None

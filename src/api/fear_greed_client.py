"""Fear & Greed Index API client."""

from typing import Dict, Any

from src.api.base_client import BaseAPIClient
from src.config.constants import FEAR_GREED_API_URL


class FearGreedClient(BaseAPIClient):
    """Client for Fear & Greed Index API."""

    def __init__(self):
        """Initialize Fear & Greed client."""
        super().__init__(FEAR_GREED_API_URL, service_name="Fear & Greed Index")

    def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get current Fear & Greed Index.

        Returns:
            Dictionary with value, classification, and timestamp
        """
        try:
            data = self.get("")
            if data.get("data") and len(data["data"]) > 0:
                fng_data = data["data"][0]
                return {
                    "value": int(fng_data.get("value", 50)),
                    "value_classification": fng_data.get(
                        "value_classification", "Neutral"
                    ),
                    "timestamp": fng_data.get("timestamp"),
                }
        except Exception:
            pass

        # Return default if API fails
        return {
            "value": 50,
            "value_classification": "Neutral",
            "timestamp": None,
        }

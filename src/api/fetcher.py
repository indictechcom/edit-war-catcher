import requests
from typing import List, Dict, Optional
from src.utils.logger import get_logger
from src.config import WIKI_API_URL
from src.config import BOT_CONTACT

logger = get_logger("fetcher")

# User-Agent is REQUIRED by Wikimedia API policy
HEADERS = {
    "User-Agent": f"EditWarCatcherBot/0.1 (contact: {BOT_CONTACT})"
}

DEFAULT_RC_PROPS = "title|ids|timestamp|user|comment|tags|flags"


def fetch_recent_changes(
    limit: int = 50,
    namespace: Optional[int] = 0
) -> List[Dict]:
    """
    Fetch recent changes from Wikipedia using MediaWiki API.

    Args:
        limit (int): Number of recent changes to fetch (max 500 for bots).
        namespace (int | None): Namespace to filter (0 = articles).
                                 None means all namespaces.

    Returns:
        List[Dict]: List of recent change records.
    """

    params = {
        "action": "query",
        "format": "json",
        "list": "recentchanges",
        "rclimit": limit,
        "rcprop": DEFAULT_RC_PROPS,
        "rcshow": "!bot",  # exclude bot edits initially
    }

    if namespace is not None:
        params["rcnamespace"] = namespace

    try:
        logger.info("Fetching recent changes from Wikipedia API")
        response = requests.get(
            WIKI_API_URL,
            params=params,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()

        data = response.json()

        if "query" not in data or "recentchanges" not in data["query"]:
            logger.error(f"Unexpected API response structure: {data}")
            return []

        changes = data["query"]["recentchanges"]

        logger.info(f"Fetched {len(changes)} recent changes")
        return changes

    except requests.exceptions.Timeout:
        logger.error("Request to Wikipedia API timed out")
        return []

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching recent changes: {e}")
        return []

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return []

    except ValueError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return []

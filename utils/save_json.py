import json
from pathlib import Path
from typing import Any

from utils.logger import logging

logger = logging.getLogger(__name__)


def save_json(
    data: Any,
    output_path: str | Path,
) -> Path:
    """Save JSON-compatible data to a file and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except (OSError, TypeError, ValueError) as error:
        logger.error("Error saving JSON to %s: %s", path, error)
        raise

    logger.info("JSON data saved successfully at %s", path)
    return path

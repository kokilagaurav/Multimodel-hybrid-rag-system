
import json
import os
import re
from typing import Any, TypedDict
from pathlib import Path

from openai import OpenAI

from config.data_config import DataConfig
from utils.logger import logging

logger = logging.getLogger(__name__)


class TokenUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class JSONBuilder:
    """Build structured, page-level JSON metadata using GLM."""

    def __init__(self):
        self._load_dotenv()
        self.interim_dir = Path(DataConfig.interim_dir)
        self.manifest_path = self.interim_dir / "images_manifest.json"

        self.document_id = "kyoto_cultural_history"
        self.document_title = "Kyoto: A Cultural History"
        self.document_author = "John Dougill"

        # Configure these through environment variables.
        api_key = os.getenv("GLM_API_KEY")
        base_url = os.getenv(
            "GLM_BASE_URL",
            "https://open.bigmodel.cn/api/paas/v4",
        )
        self.model_name = os.getenv("GLM_MODEL", "glm-4-flash")

        if not api_key:
            raise ValueError(
                "GLM_API_KEY is missing. Set it in your environment."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    @staticmethod
    def _load_dotenv():
        """Load simple KEY=VALUE entries from the repository .env file."""
        env_path = Path(__file__).resolve().parents[2] / ".env"
        if not env_path.exists():
            return

        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value

    def _load_image_manifest(self):
        """Load image metadata created by PDFLoader."""
        if not self.manifest_path.exists():
            logger.warning("Image manifest not found: %s", self.manifest_path)
            return []

        with self.manifest_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _get_page_images(self, page_number, image_records):
        """Return only images associated with the requested PDF page."""
        return [
            {
                "image_id": image["image_id"],
                "image_path": image["image_path"],
                "image_type": "embedded_image",
                "caption": None,
                "description": None,
                "related_text": None,
                "width": image.get("width"),
                "height": image.get("height"),
            }
            for image in image_records
            if image.get("page_number") == page_number
        ]

    @staticmethod
    def _extract_json(response_text: str) -> dict[str, Any]:
        """Parse a JSON object returned by GLM."""
        response_text = response_text.strip()

        # Handle responses wrapped in Markdown code fences.
        response_text = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response_text,
            flags=re.IGNORECASE,
        ).strip()

        result = json.loads(response_text)

        if not isinstance(result, dict):
            raise ValueError("GLM response must be a JSON object.")

        return result

    def _extract_page_metadata(
        self,
        page_text: str,
        page_number: int,
    ) -> tuple[dict[str, Any], TokenUsage]:
        """Ask GLM to extract structured metadata from one page."""

        if not page_text.strip():
            return (
                {
                    "content_type": "unknown",
                    "chapter": None,
                    "section": None,
                    "printed_page_label": None,
                    "structured_content": {
                        "summary": None,
                        "topics": [],
                        "entities": [],
                        "historical_events": [],
                        "dates_and_periods": [],
                        "places": [],
                        "cultural_concepts": [],
                    },
                },
                {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            )

        prompt = f"""
You are a careful historical-document information extraction system.

Extract structured metadata from the supplied page of a book about Kyoto
and Japanese cultural history.

PDF page number: {page_number}

Rules:
1. Use only evidence in the supplied page text.
2. Do not invent historical facts, names, dates, chapters, or sections.
3. Preserve uncertainty. Use null when a field cannot be determined.
4. Keep summaries concise and faithful to the page.
5. Include evidence_text for extracted entities, events, dates, places,
   and cultural concepts. Evidence must be copied from the source text
   as accurately as possible.
6. Use empty arrays when no items are supported by the text.
7. Use numeric years only when the text supports them. Do not guess
   approximate years from historical knowledge.
8. content_type must be one of:
   front_matter, chapter_text, index, bibliography, caption, table,
   mixed, unknown.
9. Return JSON only, matching the required structure.
10. Do not reproduce the complete page text in your response.

Required JSON structure:
{{
  "content_type": "unknown",
  "chapter": null,
  "section": null,
  "printed_page_label": null,
  "structured_content": {{
    "summary": null,
    "topics": [],
    "entities": [
      {{
        "entity_id": "entity_001",
        "name": "Name from the text",
        "entity_type": "person",
        "description": null,
        "evidence_text": "Supporting text"
      }}
    ],
    "historical_events": [
      {{
        "event_id": "event_001",
        "event_name": "Event from the text",
        "date_text": null,
        "start_year": null,
        "end_year": null,
        "description": null,
        "people_involved": [],
        "places_involved": [],
        "evidence_text": null
      }}
    ],
    "dates_and_periods": [
      {{
        "date_text": "Exact date or period wording",
        "start_year": null,
        "end_year": null,
        "period_type": "historical_period",
        "evidence_text": null
      }}
    ],
    "places": [
      {{
        "name": "Place from the text",
        "place_type": "city",
        "description": null,
        "evidence_text": null
      }}
    ],
    "cultural_concepts": [
      {{
        "name": "Concept from the text",
        "category": "tradition",
        "description": null,
        "evidence_text": null
      }}
    ]
  }}
}}

For entity_type, use an appropriate value such as person, organization,
place, artwork, book, or other.

For period_type, use an appropriate value such as historical_period,
calendar_date, century, or era.

For place_type, use an appropriate value such as city, region, building,
temple, shrine, or other.

For cultural concept category, use an appropriate value such as
tradition, religion, art, architecture, literature, philosophy,
festival, food, or other.

Source page text:
<page_text>
{page_text}
</page_text>
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract factual metadata from source text. "
                        "Return valid JSON only. Never invent evidence."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                f"GLM returned an empty response for page {page_number}."
            )

        usage = response.usage
        token_usage: TokenUsage = {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
            "completion_tokens": (
                getattr(usage, "completion_tokens", 0) if usage else 0
            ),
            "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0,
        }

        return self._extract_json(content), token_usage

    def build_json(self, documents, source_file):
        """Build the complete document JSON from LangChain page documents."""

        image_records = self._load_image_manifest()
        pages = []
        token_usage: dict[str, int] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "requests": 0,
        }

        for index, document in enumerate(documents, start=1):
            # PyMuPDFLoader commonly stores a zero-based page index.
            raw_page = document.metadata.get("page", index - 1)

            try:
                page_number = int(raw_page) + 1
            except (TypeError, ValueError):
                page_number = index

            page_text = document.page_content or ""

            logger.info(
                "Building structured metadata for page %d of %d",
                page_number,
                len(documents),
            )

            try:
                metadata, page_tokens = self._extract_page_metadata(
                    page_text=page_text,
                    page_number=page_number,
                )
                page_token_usage = page_tokens
                for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                    token_usage[key] += page_tokens[key]
                if page_text.strip():
                    token_usage["requests"] += 1
            except Exception:
                # Preserve the page and source text even if GLM fails.
                logger.exception(
                    "GLM extraction failed for page %d",
                    page_number,
                )
                metadata = {
                    "content_type": "unknown",
                    "chapter": None,
                    "section": None,
                    "printed_page_label": None,
                    "structured_content": {
                        "summary": None,
                        "topics": [],
                        "entities": [],
                        "historical_events": [],
                        "dates_and_periods": [],
                        "places": [],
                        "cultural_concepts": [],
                    },
                }
                page_token_usage: TokenUsage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                }

            structured_content = metadata.get("structured_content", {})

            # Avoid losing expected fields if GLM omits one.
            defaults = {
                "summary": None,
                "topics": [],
                "entities": [],
                "historical_events": [],
                "dates_and_periods": [],
                "places": [],
                "cultural_concepts": [],
            }

            for key, default in defaults.items():
                structured_content.setdefault(key, default)

            pages.append({
                "page_id": (
                    f"{self.document_id}_p{page_number:04d}"
                ),
                "page_number": page_number,
                "printed_page_label": metadata.get(
                    "printed_page_label"
                ),
                "content_type": metadata.get("content_type", "unknown"),
                "chapter": metadata.get("chapter"),
                "section": metadata.get("section"),

                # Keep the original extracted text unchanged.
                "original_text": page_text,

                "structured_content": structured_content,
                "token_usage": page_token_usage,
                "images": self._get_page_images(
                    page_number,
                    image_records,
                ),
                "tables": [],
            })

        result = {
            "schema_version": "1.0.0",
            "document": {
                "document_id": self.document_id,
                "title": self.document_title,
                "author": self.document_author,
                "source_file": Path(source_file).name,
                "language": "en",
                "total_pages": len(pages),
            },
            "processing": {
                "text_extraction_status": "completed",
                "structured_extraction_status": (
                    "completed_with_errors"
                    if any(
                        page["content_type"] == "unknown"
                        and page["original_text"].strip()
                        for page in pages
                    )
                    else "completed"
                ),
                "model_provider": "GLM",
                "model_name": self.model_name,
                "token_usage": token_usage,
            },
            "pages": pages,
        }

        logger.info(
            "JSON structure built for %d pages using %d total tokens",
            len(pages),
            token_usage["total_tokens"],
        )
        return result

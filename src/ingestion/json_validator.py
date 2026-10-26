
from pathlib import Path
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from utils.logger import logging

logger = logging.getLogger(__name__)


class Entity(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entity_id: str
    name: str
    entity_type: str
    description: str | None = None
    evidence_text: str | None = None


class HistoricalEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: str
    event_name: str
    date_text: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    description: str | None = None
    people_involved: list[str] = Field(default_factory=list)
    places_involved: list[str] = Field(default_factory=list)
    evidence_text: str | None = None


class DateOrPeriod(BaseModel):
    model_config = ConfigDict(extra="ignore")

    date_text: str
    start_year: int | None = None
    end_year: int | None = None
    period_type: str
    evidence_text: str | None = None


class Place(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    place_type: str
    description: str | None = None
    evidence_text: str | None = None


class CulturalConcept(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    category: str
    description: str | None = None
    evidence_text: str | None = None


class StructuredContent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    summary: str | None = None
    topics: list[str] = Field(default_factory=list)
    entities: list[Entity] = Field(default_factory=list)
    historical_events: list[HistoricalEvent] = Field(
        default_factory=list
    )
    dates_and_periods: list[DateOrPeriod] = Field(
        default_factory=list
    )
    places: list[Place] = Field(default_factory=list)
    cultural_concepts: list[CulturalConcept] = Field(
        default_factory=list
    )


class ImageRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    image_id: str
    image_path: str
    image_type: str = "embedded_image"
    caption: str | None = None
    description: str | None = None
    related_text: str | None = None
    width: int | None = None
    height: int | None = None


class PageRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    page_id: str
    page_number: int = Field(ge=1)
    printed_page_label: str | None = None
    content_type: Literal[
        "front_matter",
        "chapter_text",
        "index",
        "bibliography",
        "caption",
        "table",
        "mixed",
        "unknown",
    ] = "unknown"
    chapter: str | None = None
    section: str | None = None
    original_text: str
    structured_content: StructuredContent
    images: list[ImageRecord] = Field(default_factory=list)
    tables: list[dict] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    document_id: str
    title: str
    author: str
    source_file: str
    language: str = "en"
    total_pages: int = Field(ge=0)


class ProcessingMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text_extraction_status: str
    structured_extraction_status: str
    model_provider: str | None = None
    model_name: str | None = None


class HistoryDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: str
    document: DocumentMetadata
    processing: ProcessingMetadata
    pages: list[PageRecord]

    @model_validator(mode="after")
    def validate_document_consistency(self):
        """Validate relationships across pages and images."""

        if self.document.total_pages != len(self.pages):
            raise ValueError(
                "document.total_pages does not match the number of pages."
            )

        page_numbers = [page.page_number for page in self.pages]
        if len(page_numbers) != len(set(page_numbers)):
            raise ValueError("Duplicate PDF page numbers detected.")

        page_ids = [page.page_id for page in self.pages]
        if len(page_ids) != len(set(page_ids)):
            raise ValueError("Duplicate page IDs detected.")

        image_ids = [
            image.image_id
            for page in self.pages
            for image in page.images
        ]
        if len(image_ids) != len(set(image_ids)):
            raise ValueError("Duplicate image IDs detected.")

        return self


class JSONValidator:
    """Validate structured history JSON using Pydantic."""

    def validate(self, data: dict) -> dict:
        """
        Validate a JSON-compatible dictionary.

        Returns the validated dictionary.
        Raises ValidationError or ValueError if invalid.
        """
        logger.info("Starting JSON schema validation")

        try:
            validated_document = HistoryDocument.model_validate(data)
            validated_data = validated_document.model_dump(mode="json")

            logger.info(
                "JSON validation successful: %d pages",
                len(validated_data["pages"]),
            )
            return validated_data

        except Exception:
            logger.exception("JSON schema validation failed")
            raise

    def validate_file(self, file_path: str | Path) -> dict:
        """Load and validate an existing JSON file."""
        import json

        file_path = Path(file_path)

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return self.validate(data)

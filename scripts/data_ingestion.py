
import json
from pathlib import Path

from config.data_config import DataConfig
from src.ingestion.pdf_loader import PDFLoader
from src.ingestion.json_builder import JSONBuilder
from src.ingestion.json_validator import JSONValidator
from utils.logger import logging

logger = logging.getLogger(__name__)


class Ingestion:
    """Orchestrate PDF extraction, JSON building, and validation."""

    def __init__(self):
        self.pdf_loader = PDFLoader()
        self.json_builder = JSONBuilder()
        self.json_validator = JSONValidator()

        self.interim_dir = Path(DataConfig.interim_dir)
        self.output_path = self.interim_dir / "kyoto_history.json"

        self.interim_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, file_path=None):
        """
        Run the complete ingestion pipeline.

        Returns the validated JSON dictionary.
        The output file is written only after validation succeeds.
        """
        if file_path is None:
            file_path = (
                Path(DataConfig.raw_dir)
                / "kyoto-a-cultural-history_compress.pdf"
            )
        else:
            file_path = Path(file_path)

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Source PDF does not exist: {file_path}"
            )

        logger.info("Starting ingestion pipeline for %s", file_path)

        try:
            # Step 1: Extract page documents and save images.
            documents = self.pdf_loader.load_pdf(str(file_path))

            # Step 2: Build the structured JSON using GLM.
            raw_data = self.json_builder.build_json(
                documents=documents,
                source_file=file_path,
            )

            # Step 3: Validate the complete JSON structure.
            validated_data = self.json_validator.validate(raw_data)

            # Step 4: Save only validated output.
            temporary_path = self.output_path.with_suffix(".tmp")

            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(
                    validated_data,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            temporary_path.replace(self.output_path)

            logger.info(
                "Ingestion completed successfully. Output: %s",
                self.output_path,
            )

            return validated_data

        except Exception:
            logger.exception("Ingestion pipeline failed")
            raise

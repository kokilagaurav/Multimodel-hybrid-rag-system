import json
import fitz

from pathlib import Path
from config.data_config import DataConfig
from langchain_community.document_loaders import PyMuPDFLoader
from utils.logger import logging

logger = logging.getLogger(__name__)

class PDFLoader:
    def __init__(self):
        self.interim_dir = Path(DataConfig.interim_dir)
        self.image_dir = self.interim_dir / "images"
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def load_pdf(self, file_path):
        logger.info(f"Loading PDF file: {file_path}")

        try:
            loader = PyMuPDFLoader(
                file_path,
                extract_images=False,
                extract_tables="markdown",
            )

            document = loader.load()

            # New: save embedded images and their metadata
            self.extract_images(file_path)

            logger.info(
                f"Loaded {len(document)} pages from PDF file: {file_path}"
            )
            return document

        except Exception:
            logger.exception("Error during PDF loading")
            raise

    def extract_images(self, file_path):
        image_records = []

        with fitz.open(file_path) as pdf:
            for page_index in range(len(pdf)):
                page_number = page_index + 1
                page = pdf.load_page(page_index)
                seen_xrefs = set()
                image_number = 0

                for image_info in page.get_images(full=True):
                    xref = image_info[0]

                    if xref in seen_xrefs:
                        continue

                    seen_xrefs.add(xref)

                    try:
                        image_data = pdf.extract_image(xref)
                        image_number += 1

                        image_id = (
                            f"page_{page_number:04d}_img_{image_number:03d}"
                        )
                        extension = image_data["ext"]

                        image_path = (
                            self.image_dir / f"{image_id}.{extension}"
                        )
                        image_path.write_bytes(image_data["image"])

                        image_records.append({
                            "image_id": image_id,
                            "page_number": page_number,
                            "image_path": image_path.as_posix(),
                            "width": image_data["width"],
                            "height": image_data["height"],
                        })

                    except Exception:
                        logger.exception(
                            "Failed to extract image on page %s",
                            page_number,
                        )

            manifest_path = self.interim_dir / "images_manifest.json"
            manifest_path.write_text(
                json.dumps(image_records, indent=2),
                encoding="utf-8",
            )

        logger.info("Extracted %d images", len(image_records))
        return image_records
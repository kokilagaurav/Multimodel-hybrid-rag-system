from langchain_community.document_loaders import PyMuPDFLoader
from utils.logger import logging

logger = logging.getLogger(__name__)

class PDFLoader:
    def __init__(self):
        pass
    def load_pdf(self, file_path):
        logger.info(f"Loading PDF file: {file_path}")
        try:
            loader = PyMuPDFLoader(
                file_path,
                extract_images=True,          # Extracts embedded images
                extract_tables="markdown",
            )

            document = loader.load()
            logger.info(f"Loaded {len(document)} pages from PDF file: {file_path}")
            return document
        except Exception as e:
            logger.error(f"Error during PDF load for as {e}"
            )
            raise e

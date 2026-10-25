from langchain_community.document_loaders import TextLoader
from utils.logger import logging

logger = logging.getLogger(__name__)

class text_loader:
    def __init__(self):
        pass

    def load_text(self, file_path):
        try:
            logger.info(f"Loading text file: {file_path}")
            loader = TextLoader(
                file_path,
                encoding = "utf-8"
            )

            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from text file: {file_path}")

            return documents
        except Exception as e:
                    logger.error(f"Error during text load for as {e}"
                    )
                    raise e
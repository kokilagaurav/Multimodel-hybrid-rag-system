
from scripts.data_ingestion import Ingestion
from utils.logger import logging

logger = logging.getLogger(__name__)


def main():
    pipeline = Ingestion()
    result = pipeline.load_data()

    print("Ingestion completed successfully.")
    print("Pages processed:", len(result["pages"]))


if __name__ == "__main__":
    main()

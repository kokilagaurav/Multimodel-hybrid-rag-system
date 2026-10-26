from pathlib import Path

from src.ingestion.pdf_loader import PDFLoader
from config.data_config import DataConfig

data = DataConfig()
pdf_files = sorted(data.raw_dir.glob("*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No PDF files found in {data.raw_dir}")
file_path = pdf_files[0]
output_path = Path("data/interim/extracted_text.txt")


loader = PDFLoader()
documents = loader.load_pdf(str(file_path))

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    "\n\n".join(document.page_content for document in documents),
    encoding="utf-8",
)

print(f"Extracted text saved to {output_path}")

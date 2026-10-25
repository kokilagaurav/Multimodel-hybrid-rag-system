from pathlib import Path

from src.ingestion.text_loader import text_loader
from config.data_config import DataConfig

data = DataConfig()
file_path = data.interim_dir 
output_path = data.interim_dir / "extracted_text2.txt"

loader = text_loader()
documents = loader.load_text(file_path)

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    "\n\n".join(document.page_content for document in documents),
    encoding="utf-8",
)

print(f"Extracted text saved to {output_path}")

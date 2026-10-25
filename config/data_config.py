
from dataclasses import dataclass
from pathlib import Path

from config.base import PROJECT_ROOT


@dataclass(frozen=True)
class DataConfig:
    raw_dir: Path = PROJECT_ROOT / "data" / "raw" / "sample.pdf"
    interim_dir: Path = PROJECT_ROOT / "data" / "interim"
    processed_dir: Path = PROJECT_ROOT / "data" / "processed"
    chunks_dir: Path = PROJECT_ROOT / "data" / "chunks"
    evaluation_dir: Path = PROJECT_ROOT / "data" / "evaluation"

    input_format: str = "pdf"
    enable_ocr: bool = True


data_config = DataConfig()

from .base import MetadataExtractor
from .image_metadata import ImageMetadataExtractor
from .pdf_metadata import PDFMetadataExtractor
from .audio_metadata import AudioMetadataExtractor
from .office_metadata import OfficeMetadataExtractor
from pathlib import Path
 
EXTRACTORS = [
    ImageMetadataExtractor,
    PDFMetadataExtractor,
    AudioMetadataExtractor,
    OfficeMetadataExtractor
]
 
def get_extractor(file_path: str) -> MetadataExtractor:
    path = Path(file_path)
    suffix = path.suffix.lower()
    for extractor_class in EXTRACTORS:
        if suffix in extractor_class.supported_extensions:
            return extractor_class(file_path)
    raise ValueError(f"Unsupported: {path.suffix}")
 
if __name__ == "__main__":
    print("✓ Registry ready")
    for ext in EXTRACTORS:
        print(f"  - {ext.__name__}")

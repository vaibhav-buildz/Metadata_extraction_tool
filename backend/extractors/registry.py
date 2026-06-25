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
    """Factory function: returns appropriate extractor for file type"""
    path = Path(file_path)
    
    for extractor_class in EXTRACTORS:
        extractor = extractor_class(file_path)
        if extractor.is_supported():
            return extractor
    
    raise ValueError(f"Unsupported file type: {path.suffix}")


if __name__ == "__main__":
    print("✓ Extractor registry ready")
    print(f"✓ Registered extractors: {len(EXTRACTORS)}")
    for ext in EXTRACTORS:
        print(f"  - {ext.__name__}")

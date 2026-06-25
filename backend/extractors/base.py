from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class MetadataExtractor(ABC):
    """Abstract base class for extracting metadata from files"""
    
    supported_extensions: tuple = ()
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.filename = self.file_path.name
        self.file_size = self.file_path.stat().st_size
    
    @abstractmethod
    def extract(self) -> Dict[str, Any]:
        """Extract metadata from file - implemented by subclasses"""
        pass
    
    def _safe_extract(self) -> Dict[str, Any]:
        """Safe wrapper with error handling"""
        try:
            return self.extract()
        except Exception as e:
            return {
                "error": str(e),
                "file": self.filename,
                "extractor": self.__class__.__name__,
                "status": "FAILED"
            }
    
    def is_supported(self) -> bool:
        """Check if file extension is supported"""
        suffix = self.file_path.suffix.lower()
        return suffix in self.supported_extensions


if __name__ == "__main__":
    print("✓ Base extractor class ready")
    print("✓ Supported methods: extract(), _safe_extract(), is_supported()")

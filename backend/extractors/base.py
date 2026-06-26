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
    
    def verify_signature(self) -> str | None:
        """Verify that the file content matches its extension (detect spoofing)"""
        suffix = self.file_path.suffix.lower()
        try:
            with open(self.file_path, "rb") as f:
                header = f.read(16)
        except Exception as e:
            return f"Cannot read file header: {e}"
        
        if suffix in ('.jpg', '.jpeg'):
            if not header.startswith(b'\xff\xd8\xff'):
                return f"Mismatched signature for JPEG: header starts with {header[:4].hex().upper()}"
        elif suffix == '.png':
            if not header.startswith(b'\x89PNG\r\n\x1a\n'):
                return f"Mismatched signature for PNG: header starts with {header[:4].hex().upper()}"
        elif suffix == '.gif':
            if not (header.startswith(b'GIF89a') or header.startswith(b'GIF87a')):
                return "Mismatched signature for GIF"
        elif suffix == '.pdf':
            if not header.startswith(b'%PDF-'):
                return f"Mismatched signature for PDF: header starts with {header[:5].decode(errors='replace')}"
        elif suffix in ('.docx', '.xlsx', '.pptx'):
            if not header.startswith(b'PK\x03\x04'):
                return f"Mismatched signature for Office document: header starts with {header[:4].hex().upper()}"
        elif suffix == '.flac':
            if not header.startswith(b'fLaC'):
                return "Mismatched signature for FLAC"
        elif suffix == '.ogg':
            if not header.startswith(b'OggS'):
                return "Mismatched signature for OGG"
        elif suffix == '.wav':
            if not (header.startswith(b'RIFF') and header[8:12] == b'WAVE'):
                return "Mismatched signature for WAV"
        elif suffix == '.mp3':
            is_mp3 = header.startswith(b'ID3') or (len(header) > 1 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0)
            if not is_mp3:
                return f"Mismatched signature for MP3: header starts with {header[:4].hex().upper()}"
        
        return None

    def _safe_extract(self) -> Dict[str, Any]:
        """Safe wrapper with error handling"""
        try:
            metadata = self.extract()
            if not isinstance(metadata, dict):
                metadata = {}
            if "anomalies" not in metadata:
                metadata["anomalies"] = []
            
            spoof_err = self.verify_signature()
            if spoof_err:
                metadata["anomalies"].append(spoof_err)
                
            return metadata
        except Exception as e:
            return {
                "error": str(e),
                "file": self.filename,
                "extractor": self.__class__.__name__,
                "status": "FAILED",
                "anomalies": [f"Extraction failed: {str(e)}"]
            }
    
    def is_supported(self) -> bool:
        """Check if file extension is supported"""
        suffix = self.file_path.suffix.lower()
        return suffix in self.supported_extensions


if __name__ == "__main__":
    print("✓ Base extractor class ready")
    print("✓ Supported methods: extract(), _safe_extract(), is_supported(), verify_signature()")


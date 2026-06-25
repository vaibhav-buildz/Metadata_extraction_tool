from .base import MetadataExtractor
from typing import Dict, Any
import pypdf
import pdfplumber


class PDFMetadataExtractor(MetadataExtractor):
    supported_extensions = ('.pdf',)
    
    def extract(self) -> Dict[str, Any]:
        metadata = {
            "file_type": "PDF",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "document_properties": {},
            "pages": 0,
            "embedded_content": {},
            "encrypted": False,
            "anomalies": []
        }
        
        try:
            with pypdf.PdfReader(str(self.file_path)) as reader:
                metadata["pages"] = len(reader.pages)
                metadata["encrypted"] = reader.is_encrypted
                
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        metadata["document_properties"][key] = str(value)
        except Exception as e:
            metadata["document_properties"]["error"] = str(e)
        
        try:
            with pdfplumber.open(str(self.file_path)) as pdf:
                links_count = 0
                images_count = 0
                for page in pdf.pages:
                    if page.extract_links():
                        links_count += len(page.extract_links())
                    if page.images:
                        images_count += len(page.images)
                
                metadata["embedded_content"]["images"] = images_count
                metadata["embedded_content"]["links"] = links_count
        except Exception as e:
            metadata["anomalies"].append(f"Embedded content detection failed: {e}")
        
        return metadata


if __name__ == "__main__":
    print("✓ PDFMetadataExtractor class ready")
    print("✓ Extracts: document properties, pages, embedded content")

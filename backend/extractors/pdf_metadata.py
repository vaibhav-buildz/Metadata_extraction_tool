from .base import MetadataExtractor
from typing import Dict, Any
import pypdf
import pdfplumber


class PDFMetadataExtractor(MetadataExtractor):
    supported_extensions = ('.pdf',)
    
    def extract(self) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "file_type": "PDF",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "document_properties": {},
            "pages": 0,
            "embedded_content": {},
            "encrypted": False,
            "anomalies": []
        }
        
        # Scan for embedded JavaScript (forensic anomaly)
        try:
            with open(self.file_path, 'rb') as f:
                raw_content = f.read()
                if b'/JS' in raw_content or b'/JavaScript' in raw_content:
                    metadata["anomalies"].append("Embedded JavaScript detected (security risk / potential dynamic payload)")
        except Exception:
            pass
        
        try:
            reader = pypdf.PdfReader(str(self.file_path))
            metadata["pages"] = len(reader.pages)
            metadata["encrypted"] = reader.is_encrypted
            if reader.is_encrypted:
                metadata["anomalies"].append("PDF is encrypted/password-protected (limits forensic visibility)")
            if reader.metadata:
                for key, value in reader.metadata.items():
                    metadata["document_properties"][key] = str(value)
        except Exception as e:
            metadata["document_properties"]["error"] = str(e)
            metadata["anomalies"].append(f"PDF structure corrupted or unreadable: {e}")
        
        try:
            with pdfplumber.open(str(self.file_path)) as pdf:
                links_count = 0
                images_count = 0
                for page in pdf.pages:
                    if page.hyperlinks:
                        links_count += len(page.hyperlinks)
                    if page.images:
                        images_count += len(page.images)
                metadata["embedded_content"]["images"] = images_count
                metadata["embedded_content"]["links"] = links_count
        except Exception as e:
            if not metadata["encrypted"]:
                metadata["anomalies"].append(f"Content layout extraction failed: {e}")
        
        return metadata


if __name__ == "__main__":
    print("✓ PDFMetadataExtractor ready")


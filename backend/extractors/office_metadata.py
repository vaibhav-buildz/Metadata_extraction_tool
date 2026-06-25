from .base import MetadataExtractor
from typing import Dict, Any
from docx import Document
from openpyxl import load_workbook


class OfficeMetadataExtractor(MetadataExtractor):
    supported_extensions = ('.docx', '.xlsx', '.pptx')
    
    def extract(self) -> Dict[str, Any]:
        if self.file_path.suffix.lower() == '.docx':
            return self._extract_docx()
        elif self.file_path.suffix.lower() == '.xlsx':
            return self._extract_xlsx()
        else:
            return {"error": "PPTX extraction not yet implemented"}
    
    def _extract_docx(self) -> Dict[str, Any]:
        metadata = {
            "file_type": "Word Document",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "core_properties": {},
            "anomalies": []
        }
        
        try:
            doc = Document(str(self.file_path))
            props = doc.core_properties
            
            metadata["core_properties"] = {
                "author": props.author or "Not set",
                "title": props.title or "Not set",
                "subject": props.subject or "Not set",
                "keywords": props.keywords or "Not set",
                "category": props.category or "Not set",
                "comments": props.comments or "Not set",
                "created": str(props.created) if props.created else "Not set",
                "modified": str(props.modified) if props.modified else "Not set",
                "last_modified_by": props.last_modified_by or "Not set"
            }
        
        except Exception as e:
            metadata["core_properties"]["error"] = str(e)
        
        return metadata
    
    def _extract_xlsx(self) -> Dict[str, Any]:
        metadata = {
            "file_type": "Excel Spreadsheet",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "workbook_properties": {},
            "sheets": []
        }
        
        try:
            wb = load_workbook(str(self.file_path))
            props = wb.properties
            
            metadata["workbook_properties"] = {
                "creator": props.creator or "Not set",
                "title": props.title or "Not set",
                "subject": props.subject or "Not set",
                "created": str(props.created) if props.created else "Not set",
                "modified": str(props.modified) if props.modified else "Not set"
            }
            
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                metadata["sheets"].append({
                    "name": sheet_name,
                    "rows": ws.max_row,
                    "columns": ws.max_column
                })
        
        except Exception as e:
            metadata["workbook_properties"]["error"] = str(e)
        
        return metadata


if __name__ == "__main__":
    print("✓ OfficeMetadataExtractor class ready")
    print("✓ Supported formats: DOCX, XLSX, PPTX")

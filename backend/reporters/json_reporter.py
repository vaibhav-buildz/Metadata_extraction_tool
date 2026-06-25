import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


class JSONReporter:
    @staticmethod
    def generate(metadata: Dict[str, Any], output_path: str = None) -> str:
        """Generate structured JSON report"""
        report = {
            "report_version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        json_str = json.dumps(report, indent=2, default=str)
        
        if output_path:
            Path(output_path).write_text(json_str)
        
        return json_str


if __name__ == "__main__":
    print("✓ JSONReporter class ready")
    
    test_metadata = {
        "filename": "test.jpg",
        "file_type": "Image",
        "file_size_bytes": 1024000
    }
    
    json_output = JSONReporter.generate(test_metadata)
    print("\nSample output (first 200 chars):")
    print(json_output[:200] + "...")

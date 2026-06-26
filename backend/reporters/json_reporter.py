import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
 
class JSONReporter:
    @staticmethod
    def generate(metadata: Dict[str, Any], output_path: str | None = None) -> str:
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
    print("✓ JSONReporter ready")

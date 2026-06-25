from typing import Dict, Any


class CLIReporter:
    @staticmethod
    def display(metadata: Dict[str, Any]) -> None:
        """Display metadata as a formatted CLI report"""
        filename = metadata.get("filename", "Unknown")
        file_type = metadata.get("file_type", "Unknown")
        file_size = metadata.get("file_size_bytes", 0)

        print(f"\n{'='*60}")
        print(f"  FILE: {filename}")
        print(f"  TYPE: {file_type}  |  SIZE: {file_size:,} bytes")
        print(f"{'='*60}")

        skip_keys = {"filename", "file_type", "file_size_bytes", "anomalies"}

        for section, data in metadata.items():
            if section in skip_keys:
                continue
            if not data:
                continue

            print(f"\n  [{section.replace('_', ' ').upper()}]")

            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"    {key:<30} {value}")
            elif isinstance(data, list):
                for item in data:
                    print(f"    • {item}")
            else:
                print(f"    {data}")

        anomalies = metadata.get("anomalies", [])
        if anomalies:
            print(f"\n  [⚠ ANOMALIES]")
            for anomaly in anomalies:
                print(f"    ✗ {anomaly}")

        print()


if __name__ == "__main__":
    print("✓ CLIReporter class ready")

    test_metadata = {
        "filename": "test.jpg",
        "file_type": "Image",
        "file_size_bytes": 1024000,
        "basic_properties": {
            "format": "JPEG",
            "width_px": 1920,
            "height_px": 1080,
        },
        "anomalies": ["EXIF data partially stripped"],
    }

    CLIReporter.display(test_metadata)

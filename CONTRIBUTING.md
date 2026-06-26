# Contributing to Metadata Forensics Tool

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/vaibhav-buildz/metadata-forensics.git
cd metadata-forensics/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Style

- **Python**: Follow PEP 8
- **Imports**: Use absolute imports, organize with `isort`
- **Docstrings**: Use triple-quoted strings for functions

```python
def extract_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary of metadata
    """
```

## Adding a New Extractor

1. Create `backend/extractors/new_type_metadata.py`
2. Inherit from `MetadataExtractor` base class
3. Implement `extract()` method
4. Register in `backend/extractors/registry.py`
5. Test with sample files

Example:

```python
from .base import MetadataExtractor

class NewTypeExtractor(MetadataExtractor):
    supported_extensions = ('.ext1', '.ext2')
    
    def extract(self) -> Dict[str, Any]:
        return {
            "file_type": "NewType",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "properties": {}
        }
```

## Testing

```bash
# Test single extractor
python -c "from image_metadata import ImageMetadataExtractor; print('OK')"

# Test registry
python extractors/registry.py

# Manual test with CLI
python -m cli.forensics_cli analyze test_file.jpg --format cli
```

## Reporting Issues

Include:
- File type tested
- Python version
- Error message/traceback
- Sample file (if possible)

## Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add feature description"`
4. Push to branch: `git push origin feature/your-feature`
5. Open Pull Request with description

## Code Review

PRs will be reviewed for:
- Functionality
- Code quality
- Documentation
- Backward compatibility

## Questions?

Open an issue or reach out to @vaibhav-buildz

Thanks for contributing! 🎉

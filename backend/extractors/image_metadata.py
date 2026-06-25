from .base import MetadataExtractor
from typing import Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS
import piexif


class ImageMetadataExtractor(MetadataExtractor):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff')
    
    def extract(self) -> Dict[str, Any]:
        metadata = {
            "file_type": "Image",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "basic_properties": {},
            "exif_data": {},
            "anomalies": []
        }
        
        try:
            with Image.open(self.file_path) as img:
                metadata["basic_properties"] = {
                    "format": img.format,
                    "mode": img.mode,
                    "width_px": img.width,
                    "height_px": img.height,
                    "dpi": img.info.get('dpi', 'Not set'),
                    "has_transparency": img.mode in ('RGBA', 'LA', 'P')
                }
                
                if "icc_profile" in img.info:
                    metadata["has_icc_profile"] = True
            
            try:
                exif_dict = piexif.load(str(self.file_path))
                for ifd_name in ("0th", "Exif", "GPS"):
                    ifd = exif_dict[ifd_name]
                    for tag_id, value in ifd.items():
                        tag_name = piexif.TAGS[ifd_name][tag_id]["name"].decode()
                        try:
                            metadata["exif_data"][tag_name] = value.decode() if isinstance(value, bytes) else str(value)
                        except:
                            metadata["exif_data"][tag_name] = "[binary data]"
            except:
                metadata["anomalies"].append("No EXIF data found or corrupted")
        
        except Exception as e:
            metadata["basic_properties"]["error"] = str(e)
        
        return metadata


if __name__ == "__main__":
    print("✓ ImageMetadataExtractor class ready")
    print("✓ Supported formats: JPG, PNG, GIF, BMP, WebP, TIFF")

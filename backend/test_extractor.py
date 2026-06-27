from extractors.image_metadata import ImageMetadataExtractor
import json

extractor = ImageMetadataExtractor("d:/Metadata_extraction_tool/test.jpg")
metadata = extractor.extract()

if "error" in metadata.get("basic_properties", {}):
    print("ERROR FOUND:")
    print(metadata["basic_properties"]["error"])
else:
    print("NO ERROR IN BASIC PROPERTIES.")
    print("EXIF DATA:")
    print(json.dumps(metadata.get("exif_data", {}), indent=2))

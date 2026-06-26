from .base import MetadataExtractor
from typing import Dict, Any
from PIL import Image, IptcImagePlugin
import piexif


class ImageMetadataExtractor(MetadataExtractor):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff')
    
    def _parse_gps(self, gps_ifd: dict) -> Dict[str, Any]:
        """Decode EXIF GPS rational numbers to decimal degrees"""
        try:
            # tag IDs: 1 = GPSLatitudeRef, 2 = GPSLatitude, 3 = GPSLongitudeRef, 4 = GPSLongitude
            lat_val = gps_ifd.get(2)
            lat_ref = gps_ifd.get(1)
            lon_val = gps_ifd.get(4)
            lon_ref = gps_ifd.get(3)
            
            if not (lat_val and lat_ref and lon_val and lon_ref):
                return {}
            
            def to_decimal(val):
                deg, deg_div = val[0]
                min_val, min_div = val[1]
                sec, sec_div = val[2]
                return (deg / deg_div) + (min_val / (min_div * 60.0)) + (sec / (sec_div * 3600.0))
            
            lat = to_decimal(lat_val)
            lon = to_decimal(lon_val)
            
            lat_ref_str = lat_ref.decode('utf-8', errors='ignore') if isinstance(lat_ref, bytes) else str(lat_ref)
            lon_ref_str = lon_ref.decode('utf-8', errors='ignore') if isinstance(lon_ref, bytes) else str(lon_ref)
            
            if lat_ref_str.upper() == 'S':
                lat = -lat
            if lon_ref_str.upper() == 'W':
                lon = -lon
                
            return {
                "latitude": lat,
                "longitude": lon,
                "formatted": f"{abs(lat):.6f}° {lat_ref_str.upper()}, {abs(lon):.6f}° {lon_ref_str.upper()}",
                "maps_link": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            }
        except Exception:
            return {}

    def extract(self) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
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
                    "dpi": str(img.info.get('dpi', 'Not set')),
                    "has_transparency": img.mode in ('RGBA', 'LA', 'P')
                }
                
                # Check for ICC Profile
                if "icc_profile" in img.info:
                    icc = img.info["icc_profile"]
                    if len(icc) >= 128:
                        try:
                            profile_size = int.from_bytes(icc[0:4], byteorder='big')
                            version = f"{icc[8]}.{icc[9] >> 4}.{icc[9] & 0x0F}"
                            device_class = icc[12:16].decode('ascii', errors='ignore').strip()
                            color_space = icc[16:20].decode('ascii', errors='ignore').strip()
                            connection_space = icc[20:24].decode('ascii', errors='ignore').strip()
                            creator = icc[80:84].decode('ascii', errors='ignore').strip()
                            
                            class_map = {
                                'scnr': 'Input Device (Scanner/Camera)',
                                'mntr': 'Display Device (Monitor)',
                                'prtr': 'Output Device (Printer)',
                                'link': 'DeviceLink',
                                'spac': 'ColorSpace Conversion',
                                'abst': 'Abstract',
                                'nmcl': 'NamedColor'
                            }
                            metadata["icc_profile_details"] = {
                                "profile_size_bytes": profile_size,
                                "version": version,
                                "device_class": class_map.get(device_class, device_class),
                                "color_space": color_space,
                                "connection_space": connection_space,
                                "creator": creator
                            }
                        except Exception:
                            metadata["icc_profile_details"] = {"status": "Present (undecodable)"}
                    else:
                        metadata["icc_profile_details"] = {"status": "Present (undecodable)"}
                
                # Extract IPTC metadata
                try:
                    iptc_info = IptcImagePlugin.getiptcinfo(img)
                    if iptc_info:
                        iptc_tags = {
                            (2, 5): "title",
                            (2, 25): "keywords",
                            (2, 80): "creator",
                            (2, 85): "byline_title",
                            (2, 110): "credit",
                            (2, 115): "source",
                            (2, 116): "copyright",
                            (2, 120): "caption",
                            (2, 122): "writer"
                        }
                        metadata["iptc_metadata"] = {}
                        for tag, name in iptc_tags.items():
                            if tag in iptc_info:
                                val = iptc_info[tag]
                                if isinstance(val, list):
                                    decoded_vals = [x.decode('utf-8', errors='replace') if isinstance(x, bytes) else str(x) for x in val]
                                    metadata["iptc_metadata"][name] = ", ".join(decoded_vals)
                                else:
                                    metadata["iptc_metadata"][name] = val.decode('utf-8', errors='replace') if isinstance(val, bytes) else str(val)
                except Exception:
                    pass
                
                # Load EXIF data (only if file extension supports EXIF natively or if EXIF marker exists)
                is_jpeg = self.file_path.suffix.lower() in ('.jpg', '.jpeg', '.tiff')
                try:
                    exif_dict = piexif.load(str(self.file_path))
                    exif_found = False
                    
                    # Parse standard EXIF directories
                    for ifd_name in ("0th", "Exif", "GPS"):
                        ifd = exif_dict.get(ifd_name, {})
                        for tag_id, value in ifd.items():
                            exif_found = True
                            if tag_id in piexif.TAGS[ifd_name]:
                                tag_name = piexif.TAGS[ifd_name][tag_id]["name"]
                            else:
                                tag_name = f"UnknownTag_{tag_id}"
                            
                            try:
                                metadata["exif_data"][tag_name] = value.decode('utf-8', errors='replace') if isinstance(value, bytes) else str(value)
                            except Exception:
                                metadata["exif_data"][tag_name] = "[binary data]"
                    
                    # Parse specific GPS details
                    if exif_dict.get("GPS"):
                        gps_details = self._parse_gps(exif_dict["GPS"])
                        if gps_details:
                            metadata["gps_coordinates"] = gps_details
                    
                    # Tampering Checks
                    # 1. Software checks
                    software = exif_dict.get("0th", {}).get(305) or exif_dict.get("0th", {}).get(11)
                    if software:
                        soft_str = software.decode('utf-8', errors='ignore') if isinstance(software, bytes) else str(software)
                        soft_str_lower = soft_str.lower()
                        editing_tools = ['photoshop', 'gimp', 'lightroom', 'canva', 'paint.net', 'corel', 'affinity', 'snapseed', 'instagram']
                        for tool in editing_tools:
                            if tool in soft_str_lower:
                                metadata["anomalies"].append(f"Image edited with software: {soft_str} (possible manipulation)")
                                break
                    
                    # Remove exif_data block if empty
                    if not metadata["exif_data"]:
                        del metadata["exif_data"]
                        if is_jpeg:
                            metadata["anomalies"].append("EXIF metadata stripped (loss of source camera forensics)")
                
                except Exception:
                    # Clean up empty exif_data
                    if "exif_data" in metadata:
                        del metadata["exif_data"]
                    if is_jpeg:
                        metadata["anomalies"].append("EXIF metadata stripped (loss of source camera forensics)")
        
        except Exception as e:
            metadata["basic_properties"]["error"] = str(e)
        
        return metadata


if __name__ == "__main__":
    print("✓ ImageMetadataExtractor class ready")
    print("✓ Supported formats: JPG, PNG, GIF, BMP, WebP, TIFF")


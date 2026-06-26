from .base import MetadataExtractor
from typing import Dict, Any
import mutagen


class AudioMetadataExtractor(MetadataExtractor):
    supported_extensions = ('.mp3', '.m4a', '.wav', '.flac', '.ogg', '.wma')
    
    def extract(self) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "file_type": "Audio",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "audio_properties": {},
            "audio_tags": {},
            "id3_tags": {},  # Keep for backward compatibility
            "anomalies": []
        }
        
        try:
            audio = mutagen.File(str(self.file_path))
            if audio is not None:
                # Audio properties
                if hasattr(audio.info, 'length'):
                    metadata["audio_properties"]["duration_seconds"] = int(audio.info.length)
                    # Convert to human-readable duration
                    m, s = divmod(int(audio.info.length), 60)
                    metadata["audio_properties"]["duration"] = f"{m:02d}:{s:02d}"
                if hasattr(audio.info, 'bitrate') and audio.info.bitrate:
                    metadata["audio_properties"]["bitrate_bps"] = audio.info.bitrate
                    metadata["audio_properties"]["bitrate"] = f"{audio.info.bitrate // 1000} kbps"
                if hasattr(audio.info, 'channels'):
                    metadata["audio_properties"]["channels"] = audio.info.channels
                if hasattr(audio.info, 'sample_rate'):
                    metadata["audio_properties"]["sample_rate"] = f"{audio.info.sample_rate} Hz"
                
                # Check low bitrate anomaly (less than 96kbps)
                if hasattr(audio.info, 'bitrate') and audio.info.bitrate and audio.info.bitrate < 96000:
                    metadata["anomalies"].append(f"Extremely low bitrate: {audio.info.bitrate // 1000} kbps (indicates high compression or low-quality recording)")
                
                # Extract tags
                for key in audio.keys():
                    try:
                        val = audio[key]
                        # Clean up value display for mutagen lists/objects
                        if isinstance(val, list):
                            val_str = ", ".join(str(x) for x in val)
                        else:
                            val_str = str(val)
                        
                        metadata["audio_tags"][key] = val_str
                        metadata["id3_tags"][key] = val_str
                    except Exception:
                        metadata["audio_tags"][key] = "[binary]"
                        metadata["id3_tags"][key] = "[binary]"
                
                # Anomaly: No metadata tags
                is_mp3 = self.file_path.suffix.lower() == '.mp3'
                if is_mp3 and not metadata["audio_tags"]:
                    metadata["anomalies"].append("No ID3 tags found (metadata might be stripped)")
            else:
                metadata["anomalies"].append("Mutagen could not parse the audio structure")
        except Exception as e:
            metadata["audio_properties"]["error"] = str(e)
            metadata["anomalies"].append(f"Audio extraction error: {e}")
        
        # If no id3_tags/audio_tags were found, remove empty dicts to keep output clean
        if not metadata["audio_tags"]:
            del metadata["audio_tags"]
            del metadata["id3_tags"]
            
        return metadata


if __name__ == "__main__":
    print("✓ AudioMetadataExtractor ready")


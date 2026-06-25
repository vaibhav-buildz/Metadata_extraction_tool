from .base import MetadataExtractor
from typing import Dict, Any
import mutagen


class AudioMetadataExtractor(MetadataExtractor):
    supported_extensions = ('.mp3', '.m4a', '.wav', '.flac', '.ogg', '.wma')
    
    def extract(self) -> Dict[str, Any]:
        metadata = {
            "file_type": "Audio",
            "filename": self.filename,
            "file_size_bytes": self.file_size,
            "audio_properties": {},
            "id3_tags": {},
            "anomalies": []
        }
        
        try:
            audio = mutagen.File(str(self.file_path))
            
            if audio is not None:
                if hasattr(audio.info, 'length'):
                    metadata["audio_properties"]["duration_seconds"] = int(audio.info.length)
                if hasattr(audio.info, 'bitrate'):
                    metadata["audio_properties"]["bitrate"] = audio.info.bitrate
                if hasattr(audio.info, 'channels'):
                    metadata["audio_properties"]["channels"] = audio.info.channels
                if hasattr(audio.info, 'sample_rate'):
                    metadata["audio_properties"]["sample_rate"] = audio.info.sample_rate
                
                for key in audio.keys():
                    try:
                        metadata["id3_tags"][key] = str(audio[key])
                    except:
                        metadata["id3_tags"][key] = "[binary data]"
                
                if not metadata["id3_tags"]:
                    metadata["anomalies"].append("No ID3 tags found")
        
        except Exception as e:
            metadata["audio_properties"]["error"] = str(e)
        
        return metadata


if __name__ == "__main__":
    print("✓ AudioMetadataExtractor class ready")
    print("✓ Supported formats: MP3, M4A, WAV, FLAC, OGG, WMA")

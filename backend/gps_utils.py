def convert_gps_to_decimal(gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref):
    """
    Converts raw GPS coordinates from EXIF data to decimal degrees format.

    Args:
        gps_latitude: Tuple of tuples (degrees, minutes, seconds), e.g., ((28, 1), (32, 1), (7, 1))
        gps_latitude_ref: String "N" or "S"
        gps_longitude: Tuple of tuples (degrees, minutes, seconds), e.g., ((77, 1), (23, 1), (8, 1))
        gps_longitude_ref: String "E" or "W"

    Returns:
        dict: A dictionary containing decimal latitude, longitude, and a human-readable string.
              Returns None if the input data is invalid.
    """
    try:
        # Validate inputs
        if not all([gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref]):
            raise ValueError("Missing GPS data")
            
        def to_degrees(value):
            """Helper to convert a single EXIF GPS tuple to decimal degrees."""
            # Each component is typically a tuple of (numerator, denominator)
            d_num, d_den = value[0]
            m_num, m_den = value[1]
            s_num, s_den = value[2]
            
            degrees = d_num / d_den if d_den != 0 else 0
            minutes = m_num / m_den if m_den != 0 else 0
            seconds = s_num / s_den if s_den != 0 else 0
            
            return degrees + (minutes / 60.0) + (seconds / 3600.0)

        # Convert raw tuples to decimal values
        lat = to_degrees(gps_latitude)
        lon = to_degrees(gps_longitude)
        
        # Format the readable string before applying sign
        # We round to 4 decimal places for consistency
        readable_lat = f"{lat:.4f}° {gps_latitude_ref.upper()}"
        readable_lon = f"{lon:.4f}° {gps_longitude_ref.upper()}"
        readable_str = f"{readable_lat}, {readable_lon}"
        
        # Apply correct sign based on hemisphere (South and West are negative)
        if gps_latitude_ref.upper() == 'S':
            lat = -lat
        if gps_longitude_ref.upper() == 'W':
            lon = -lon
            
        return {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "readable": readable_str
        }
        
    except (IndexError, TypeError, ValueError, ZeroDivisionError, AttributeError) as e:
        print(f"Error converting GPS coordinates: {e}")
        return None

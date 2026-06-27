from gps_utils import convert_gps_to_decimal
import json

# Example input from your request
gps_latitude = ((28, 1), (32, 1), (7, 1))
gps_latitude_ref = "N"
gps_longitude = ((77, 1), (23, 1), (8, 1))
gps_longitude_ref = "E"

print("--- Valid Input Example ---")
result = convert_gps_to_decimal(gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref)
print(json.dumps(result, indent=2))

print("\n--- Southern/Western Hemisphere Example ---")
gps_lat_s = ((34, 1), (36, 1), (15, 1))
gps_lat_ref_s = "S"
gps_lon_w = ((58, 1), (22, 1), (54, 1))
gps_lon_ref_w = "W"
result_sw = convert_gps_to_decimal(gps_lat_s, gps_lat_ref_s, gps_lon_w, gps_lon_ref_w)
print(json.dumps(result_sw, indent=2))

print("\n--- Missing Data Error Example ---")
result_err = convert_gps_to_decimal(None, "N", gps_longitude, "E")
print(f"Result: {result_err}")

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

def get_location_info(address):
    if not isinstance(address, str) or not address.strip():
        raise ValueError("Invalid address. Address must be a non-empty string.")
    
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.geocode(address)
        if location is None:
            raise ValueError("Address could not be geocoded.")
        return {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'address': location.address
        }
    except GeocoderServiceError as e:
        raise RuntimeError(f"Geocoding service error: {e}")

# Example usage
if __name__ == "__main__":
    try:
        info = get_location_info("1600 Amphitheatre Parkway, Mountain View, CA")
        print(info)
    except (ValueError, RuntimeError) as e:
        print(e)
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_location_info(address, user_agent="geoapiExercises"):
    """
    Get location information for a given address.

    Parameters:
    - address (str): The address to geocode.
    - user_agent (str): The user agent to use for the geocoding request.

    Returns:
    - dict: A dictionary containing latitude, longitude, and address, or an error message.
    """
    geolocator = Nominatim(user_agent=user_agent)
    
    try:
        location = geolocator.geocode(address)
        if location:
            return {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': location.address
            }
        else:
            return {'error': 'Location not found.'}
    except GeocoderTimedOut:
        return {'error': 'Geocoding service timed out. Please try again.'}
    except Exception as e:
        return {'error': str(e)}

# Example usage
if __name__ == '__main__':
    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    location_info = get_location_info(address)
    print(location_info)
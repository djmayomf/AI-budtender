from geopy.geocoders import Nominatim

def get_location_info(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    return {
        'latitude': location.latitude,
        'longitude': location.longitude,
        'address': location.address
    }

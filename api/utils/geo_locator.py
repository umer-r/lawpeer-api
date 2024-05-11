"""
    Util file; Contains functions for geo-location purposes.

    External Libraries:
        - geopy.geocoders.Nominatim: A geocoding service provided by OpenStreetMap (OSM) that provides data for reverse geocoding.

    Function Names:
        - get_address
        
    # Example usage
        latitude = 32.81591
        longitude = 73.86236
        print(get_address(latitude, longitude))
"""

# Lib Imports:
from geopy.geocoders import Nominatim

# ----------------------------------------------- #

# Initialize geolocator:
## Bug fix: SSL cert error, https://stackoverflow.com/a/47091697
geolocator = Nominatim(user_agent="geo_locator", scheme='http')

def get_address(latitude, longitude):
    """
    Function to get address from latitude and longitude.

    Parameters:
        - latitude (float): The latitude coordinate.
        - longitude (float): The longitude coordinate.

    Returns:
        - country (str): The country name.
        - city (str): The city name.
        - postal_code (str or None): The postal code.
        - full_address (str): The complete address.
    """
    
    location = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)
    address = location.raw
    full_address = location.address

    country = address.get('address', {}).get('country', '')
    city = address.get('address', {}).get('city') or address.get('address', {}).get('residential') or address.get('address', {}).get('town', '')
    postal_code = address.get('address', {}).get('postcode', None)

    return country, city, postal_code, full_address

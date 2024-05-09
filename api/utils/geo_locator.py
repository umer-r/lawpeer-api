from geopy.geocoders import Nominatim

# Initialize geolocator
geolocator = Nominatim(user_agent="geo_locator")

# Function to get address from latitude and longitude
def get_address(latitude, longitude):
    location = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)
    address = location.raw
    full_address = location.address

    country = address.get('address', {}).get('country', '')
    city = address.get('address', {}).get('city') or address.get('address', {}).get('residential') or address.get('address', {}).get('town', '')
    postal_code = address.get('address', {}).get('postcode', None)

    return country, city, postal_code, full_address

# # Example usage
# latitude = 32.81591
# longitude = 73.86236
# print(get_address(latitude, longitude))
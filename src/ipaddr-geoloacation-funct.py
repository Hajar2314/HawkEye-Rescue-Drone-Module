import requests

def get_location_info():
    """Fetches the approximate location (latitude, longitude, city, region, country)."""
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()

        loc = data.get("loc")  # Format: "latitude,longitude"
        city = data.get("city")
        region = data.get("region")
        country = data.get("country")

        if loc:
            latitude, longitude = loc.split(',')
            return {
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "region": region,
                "country": country
            }
        else:
            return {"error": "Could not determine location"}

    except requests.RequestException as e:
        return {"error": f"Error fetching location: {e}"}

# Example usage:
location_info = get_location_info()
print(location_info)

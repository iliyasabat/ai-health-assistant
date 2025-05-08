from PIL import Image
from pyzbar.pyzbar import decode
import requests

def decode_barcode(image):
    decoded_objects = decode(image)
    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None

def get_food_info_from_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 1:
            product = data['product']
            name = product.get('product_name', 'Unknown')
            nutriments = product.get('nutriments', {})
            calories = nutriments.get('energy-kcal_100g', 'N/A')
            protein = nutriments.get('proteins_100g', 'N/A')
            carbs = nutriments.get('carbohydrates_100g', 'N/A')
            fat = nutriments.get('fat_100g', 'N/A')
            return {
                'name': name,
                'calories_per_100g': calories,
                'protein_per_100g': protein,
                'carbs_per_100g': carbs,
                'fat_per_100g': fat
            }
    return None 
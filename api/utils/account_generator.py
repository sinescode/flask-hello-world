import random
import string
import requests
from datetime import datetime
import re

def is_english(s):
    """Check if string contains only English letters"""
    return bool(re.match('^[a-z]+$', s))

def clean_name(name):
    """Convert name to lowercase and remove non-English characters"""
    # Convert to lowercase
    name = name.lower()
    # Remove any non-English letters
    name = re.sub('[^a-z]', '', name)
    return name

def generate_username_from_name(first_name, last_name):
    # Clean the names first
    first_name = clean_name(first_name)
    last_name = clean_name(last_name)
    
    # Skip if names are empty after cleaning
    if not first_name or not last_name:
        return generate_random_username()
    
    # Generate username based on name (e.g., "jennie123" or "jnichols42")
    base = random.choice([
        first_name,
        last_name,
        f"{first_name[0]}{last_name}",
        f"{first_name}{last_name[0]}"
    ])
    
    # Add some random digits (1-4 digits)
    digits = ''.join(random.choice(string.digits) for _ in range(random.randint(1, 4)))
    return f"{base}{digits}"

def fetch_random_user():
    try:
        response = requests.get('https://randomuser.me/api/?nat=us,gb,au,ca')  # Only English-speaking countries
        if response.status_code == 200:
            data = response.json()
            user_data = data['results'][0]
            
            # Get and clean names
            first_name = clean_name(user_data['name']['first'])
            last_name = clean_name(user_data['name']['last'])
            
            # If names are empty after cleaning, try again
            if not first_name or not last_name:
                return fetch_random_user()
                
            return {
                'first_name': first_name,
                'last_name': last_name,
                'gender': user_data['gender']
            }
    except Exception as e:
        print(f"Error fetching random user: {e}")
    return None

def generate_random_username(min_length=7, max_length=17):
    length = random.randint(min_length, max_length)
    letters = ''.join(random.choice(string.ascii_lowercase) for _ in range(length-1))
    digit = random.choice(string.digits)
    return letters + digit
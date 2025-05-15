import random
import string
import secrets

def generate_random_password(length=12, include_uppercase=True, include_lowercase=True, 
                           include_digits=True, include_special=True, special_chars="!@#$%^&*"):
    if length < 4:
        raise ValueError("Password length must be at least 4 characters")
    
    char_pool = ""
    requirements = []
    
    if include_uppercase:
        char_pool += string.ascii_uppercase
        requirements.append(lambda p: any(c.isupper() for c in p))
    if include_lowercase:
        char_pool += string.ascii_lowercase
        requirements.append(lambda p: any(c.islower() for c in p))
    if include_digits:
        char_pool += string.digits
        requirements.append(lambda p: any(c.isdigit() for c in p))
    if include_special:
        char_pool += special_chars
        requirements.append(lambda p: any(c in special_chars for c in p))
    
    if not char_pool:
        raise ValueError("At least one character set must be included")
    
    while True:
        password = ''.join(secrets.choice(char_pool) for _ in range(length))
        if all(req(password) for req in requirements):
            return password
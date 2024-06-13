from cryptography.fernet import Fernet
import re

# Function to encrypt a URL
def encrypt_url(url, key):
    cipher_suite = Fernet(key)
    encrypted_url = cipher_suite.encrypt(url.encode())
    return encrypted_url.decode()

# Function to read, encrypt, and write URLs back to the file
def encrypt_urls_in_file(file_path):
    # Generate a key for encryption
    key = Fernet.generate_key()
    with open('key.txt', 'wb') as key_file:
        key_file.write(key)

    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find URLs in the content
    urls = re.findall(r'https?://[^\s]+', content)

    # Encrypt URLs and replace them in the content
    for url in urls:
        encrypted_url = encrypt_url(url, key)
        content = content.replace(url, encrypted_url)

    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Path to your Markdown file
file_path = 'testtt.md'
encrypt_urls_in_file(file_path)
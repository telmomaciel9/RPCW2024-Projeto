from cryptography.fernet import Fernet
import re

# Function to decrypt a URL
def decrypt_url(encrypted_url, key):
    cipher_suite = Fernet(key)
    decrypted_url = cipher_suite.decrypt(encrypted_url.encode())
    return decrypted_url.decode()

# Function to read, decrypt, and write URLs back to the file
def decrypt_urls_in_file(file_path, key_path):
    # Read the encryption key from key.txt
    with open(key_path, 'r') as key_file:
        key = key_file.readline().strip().encode()

    updated_content = []

    # Process the file line by line
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Skip lines starting with #
            if not line.startswith('#'):
                # Find potential encrypted URLs in the line
                encrypted_urls = re.findall(r'[a-zA-Z0-9_-]+={0,2}', line)
                for encrypted_url in encrypted_urls:
                    try:
                        decrypted_url = decrypt_url(encrypted_url, key)
                        line = line.replace(encrypted_url, decrypted_url)
                    except Exception as e:
                        print(f"Error decrypting URL {encrypted_url}: {e}")
            updated_content.append(line)

    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_content)

file_path = 'testtt.md'
key_path = 'key.txt'

decrypt_urls_in_file(file_path, key_path)
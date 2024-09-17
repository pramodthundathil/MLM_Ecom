import requests

import hmac
import base64
import hashlib
import time
import certifi
 
secret_key_timestamp = str(int(round(time.time() * 1000)))
key = 'd2fe1d99-6298-4af2-8cc5-d97dcf46df30'
key_bytes = key.encode('utf-8')  # Convert the key to bytes
 
message = secret_key_timestamp.encode('utf-8')
dig = hmac.new(key_bytes, message, hashlib.sha256).digest()
 
secret_key = base64.b64encode(dig).decode()
 
# Print the secret key and secret timestamp
print("Secret Key:", secret_key)
print("Secret Timestamp:", secret_key_timestamp)

url = "https://staging.eko.in:25002/ekoapi/v1/pan/verify"

payload='pan_number=FPAPA6382H&purpose=1&initiator_id=9962981729&purpose_desc=onboarding'
headers = {
  'Content-Type': 'application/json',
  'developer_key': 'becbbce45f79c6f5109f848acd540567',
  'secret-key': secret_key,
  'secret-key-timestamp': secret_key_timestamp
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
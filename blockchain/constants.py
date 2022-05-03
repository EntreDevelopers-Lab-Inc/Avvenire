# set the pinata base url
PINATA_BASE_URL = 'https://av.mypinata.cloud/ipfs'

BASE_URI = (
    f"{PINATA_BASE_URL}/QmRcNTkZopCYTW6N7AJM4aWTCtisUdTAbCQRwsxWfD4jSL/"
)
LOAD_URI = (
    f"{PINATA_BASE_URL}/Qme4pwMxwMJobSuTCqvczJCgmuM54EHBVtrEVqKtsjYWos"
)

# create a file extension
EXTENSION = 'PNG'

# no, we don't need all three, but I am storing my keys here anyway
PINATA_HEADERS = {
    'pinata_api_key': '2bcfa1e161ab3e38f6b3',
    'pinata_secret_api_key': '0d6c5bf6a2423b87d78abb9aa8f5bce5ecfb204987292deba4ea04a220fded1f',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI0N2Q1YTQzNi01ODRkLTQyZGItYTJlMy01ZjBiMjUwOWE4M2QiLCJlbWFpbCI6Im9taXJlbGVzMDExQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImlkIjoiTllDMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2V9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiIyYmNmYTFlMTYxYWIzZTM4ZjZiMyIsInNjb3BlZEtleVNlY3JldCI6IjBkNmM1YmY2YTI0MjNiODdkNzhhYmI5YWE4ZjViY2U1ZWNmYjIwNDk4NzI5MmRlYmE0ZWEwNGEyMjBmZGVkMWYiLCJpYXQiOjE2NTE1ODEzMDZ9.uC9CMK8y_1BceMw3LfG0z8Tgh0rMNKBWip-QKr-Cq0Y'
}

WAIT_BLOCKS = 1

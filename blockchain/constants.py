# set the pinata base url
PINATA_BASE_URL = 'https://gateway.pinata.cloud/ipfs'

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
    'pinata_api_key': 'aade4cbe5134b606dd5c',
    'pinata_secret_api_key': 'ba265b8f30273816ebe99d2b401b2c790bad621bd0dd31b4b5d9cca507a08272',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJhMDM3N2IwZi1mMGQ4LTQzYjAtOWQ1My0yZTljNDExZmY4OGEiLCJlbWFpbCI6ImFkbWluQGVudHJlZGV2ZWxvcGVyc2xhYi5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGluX3BvbGljeSI6eyJyZWdpb25zIjpbeyJpZCI6Ik5ZQzEiLCJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MX1dLCJ2ZXJzaW9uIjoxfSwibWZhX2VuYWJsZWQiOmZhbHNlfSwiYXV0aGVudGljYXRpb25UeXBlIjoic2NvcGVkS2V5Iiwic2NvcGVkS2V5S2V5IjoiYWFkZTRjYmU1MTM0YjYwNmRkNWMiLCJzY29wZWRLZXlTZWNyZXQiOiJiYTI2NWI4ZjMwMjczODE2ZWJlOTlkMmI0MDFiMmM3OTBiYWQ2MjFiZDBkZDMxYjRiNWQ5Y2NhNTA3YTA4MjcyIiwiaWF0IjoxNjQ3Mjk0NDY2fQ.RBT6vSylcopEHsg1QB2SwrCE5J5E9Zayw5br_MV2oAo'
}

WAIT_BLOCKS = 1

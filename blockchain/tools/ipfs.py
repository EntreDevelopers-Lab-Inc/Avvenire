from .constants import PINATA_BASE_URL, PINATA_HEADERS, EXTENSION
import ipfshttpclient
import requests
import io

# set the pinning endpoint
PINNING_ENDPOINT = 'https://api.pinata.cloud/pinning/pinByHash'


def upload_to_ipfs(image):
    # get the image bytes
    buf = io.BytesIO()
    image.save(buf, format=EXTENSION)
    art_bytes = buf.getvalue()

    # create a hash using bytecode and upload it to the local ipfs node
    with ipfshttpclient.connect() as client:
        image_hash = client.add_bytes(art_bytes)

    # upload the image hash to pinata: https://docs.pinata.cloud/api-pinning/pin-by-hash
    resp = requests.post(PINNING_ENDPOINT, headers=PINATA_HEADERS, body={
                         'hashToPin': image_hash})

    # add some error handling for the response
    if resp.status_code > 299:
        return None

    # make a pinata link with the image hash
    pinata_link = f"{PINATA_BASE_URL}/image_hash"

    return pinata_link

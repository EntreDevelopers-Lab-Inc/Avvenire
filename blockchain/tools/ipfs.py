try:
    from blockchain.constants import PINATA_BASE_URL, PINATA_HEADERS, EXTENSION
except ImportError:
    from constants import PINATA_BASE_URL, PINATA_HEADERS, EXTENSION

import ipfshttpclient
import requests
import json
import io

# set the pinning endpoint
PINNING_ENDPOINT = 'https://api.pinata.cloud/pinning/pinByHash'
PIN_FILE_ENDPOINT = 'https://api.pinata.cloud/pinning/pinJSONtoIPFS'


def upload_to_ipfs(data, extension=EXTENSION):
    # get the data bytes
    buf = io.BytesIO()

    if extension:
        data.save(buf, format=extension)
        file_bytes = buf.getvalue()

        # create a hash using bytecode and upload it to the local ipfs node
        with ipfshttpclient.connect() as client:
            data_hash = client.add_bytes(file_bytes)

        # upload the data hash to pinata: https://docs.pinata.cloud/api-pinning/pin-by-hash
        resp = requests.post(PINNING_ENDPOINT, headers=PINATA_HEADERS, data={
                             'hashToPin': data_hash})
    else:
        # it is not that dense, so just upload the data directly
        print(data)
        resp = resp = requests.post(
            PIN_FILE_ENDPOINT, headers=PINATA_HEADERS, data=json.loads(data.decode('utf-8')))

        # for testing
        print(resp.json())

        data_hash = resp.json()['IpfsHash']

    # add some error handling for the response
    if resp.status_code > 299:
        return None

    # make a pinata link with the data hash
    pinata_link = f"{PINATA_BASE_URL}/{data_hash}"

    return pinata_link

// function to show an nft from ipfs
function revealNFT(uri) {
    // get the image address on the screen
    var imageTag = $('#nft-img');

    imageTag.setAttribute('src', uri);
}

// function to get an NFT's URI
function getURI(tokenId) {

}

// function to mint nft
function mintNFT() {
    // call the contract from the user's current address (this is just test code)
    CONTRACT.createCollectible(123, 'https://gateway.pinata.cloud/ipfs/QmSsYRx3LpDAb1GZQm7zZ1AuHZjfbPkD6J7s9r41xu1mf8').then(function (transactionResponse) {
        alert('created NFT transaction');

        // wait for the event to respond
        transactionResponse.wait(CONFIRMED_BLOCKS).then(function (transactionReceipt) {
            alert('NFT creation confirmed!');
            // once we have the receipt, we can show the image

        });

    });
}


// listen for event: https://docs.ethers.io/v5/api/contract/contract/#Contract--events

// need to verify with metamask: https://docs.metamask.io/guide/registering-function-names.html

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
async function mintNFTs(amount) {
    // get the gas price
    var feeData = await CONTRACT_PROVIDER.getFeeData();  // may need to update to ethers 5.4 for this --> will see
    var maxFeePerGas = parseInt(ethers.utils.formatUnits(feeData.maxFeePerGas, "gwei"));

    // get the total cost
    var totalCost = (PRICE * amount) + (GAS_LIMIT * maxFeePerGas);

    // call the contract from the user's current address (this is just test code)
    // https://docs.ethers.io/v5/api/utils/transactions/
    CONTRACT.mintNFTs(2, {value: totalCost, gasLimit: GAS_LIMIT, type: TRANSACTION_TYPE}).then(function (transactionResponse) {
        alert('created NFT transaction');

        // wait for the event to respond
        transactionResponse.wait(CONFIRMED_BLOCKS).then(function (transactionReceipt) {
            alert('NFT creation confirmed!');
            // once we have the receipt, we can show the image

        });

    });
}


// listen for event: https://docs.ethers.io/v5/api/contract/contract/#Contract--events

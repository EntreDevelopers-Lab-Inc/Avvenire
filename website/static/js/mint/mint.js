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
async function mintNFTs(amount, gasLimit=GAS_LIMIT) {
    // get the gas price
    var feeData = await CONTRACT_PROVIDER.getFeeData();  // may need to update to ethers 5.4 for this --> will see
    var maxFeePerGas = parseInt(ethers.utils.formatUnits(feeData.maxFeePerGas, "gwei"));

    // get the total cost = price * amount purchased + allowable gas cost in ETH
    var totalCost = (PRICE * amount) + (maxFeePerGas * gasLimit / GWEI_PER_ETH);

    // make the total cost a string for the parse ether utilty
    totalCost = totalCost.toString();

    // call the contract from the user's current address (this is just test code)
    // https://docs.ethers.io/v5/api/utils/transactions/
    // https://stackoverflow.com/questions/68198724/how-would-i-send-an-eth-value-to-specific-smart-contract-function-that-is-payabl
    CONTRACT.mintNFTs(2, {value: ethers.utils.parseEther(totalCost), gasLimit: GAS_LIMIT, type: TRANSACTION_TYPE}).then(function (transactionResponse) {
        alert('created NFT transaction');

        // wait for the event to respond
        transactionResponse.wait(CONFIRMED_BLOCKS).then(function (transactionReceipt) {
            alert('NFT creation confirmed!');
            // once we have the receipt, we can show the image

        });

    });
}


// listen for event: https://docs.ethers.io/v5/api/contract/contract/#Contract--events

/*
NOTES
- where should we allow the user to set the gas limit?
- what should we do on a transaction success?
- what should we do on a transaction failure?
*/

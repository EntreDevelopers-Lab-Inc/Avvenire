// need to verify with metamask: https://docs.metamask.io/guide/registering-function-names.html

// get some constants
var PRICE;  // figure out how to access structs


// function to get the mint price
// mint order: 1000 DA (3) --> WL (2) --> public (2000)
// this should also set the min/max/value of the input button
async function getMintPrice()
{
    // contract data
    var config;
    var price;
    var whitelisted;

    // input box data
    var max;
    var value;


    // get the whitelist information
    await CONTRACT.allowlist(window.ethereum.selectedAddress).then(function (resp) {
        // set whether this address is whitelisted
        whitelisted = ethers.utils.formatUnits(resp) != 0;
    });

    // get the sale information
    await CONTRACT.saleConfig().then(
        function (resp) {
            config = resp;
        });

    // check if the auction is on with saleConfig.auctionSaleStartTime <= block.time_stamp
    if (parseFloat(ethers.utils.formatEther(config[0])) > 0)  // this will be set to 0 when the auction is over
    {
        CONTRACT.AUCTION_START_PRICE().then(
            function (resp) {
                price = resp;
            });

        // set the max and value
        max = 3;
        value = max;
    }
    // check if the user is whitelisted and the price is greater than 0
    else if ((parseFloat(ethers.utils.formatEther(config[2])) > 0) && (whitelisted))
    {
        // if the user is whitelisted saleConfig.mintlistPrice
        price = config[2];

        max = 2;
        value = max;
    }
    // else, use the public sale price by calling saleConfig.publicPrice
    else
    {
        price = config[3];

        max = 2000;
        value = 5;
    }

    // convert the price to eth from gwei
    price = parseFloat(ethers.utils.formatEther(price));

    // change the max and value
    $('#amount').attr('max', max);
    $('#amount').val(value);

    // set the global variable
    PRICE = price;
}


// function to set the total price
async function setTotalCost()
{
    // get the amount
    var amount = parseInt($('#amount').val());

    // set the initial total cost
    $('#total-cost').text((PRICE * amount).toFixed(3));
}



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
async function mintNFTs(gasLimit=GAS_LIMIT) {
    // get the amount from the input box
    var amount = $('#amount').val();

    // get the gas price
    var feeData = await CONTRACT_PROVIDER.getFeeData();  // may need to update to ethers 5.4 for this --> will see
    var maxFeePerGas = parseInt(ethers.utils.formatUnits(feeData.maxFeePerGas, "gwei"));

    // get the total cost = price * amount purchased + allowable gas cost in ETH
    var totalCost = (PRICE * amount)/* + (maxFeePerGas * gasLimit / GWEI_PER_ETH)*/;

    // make the total cost a string for the parse ether utilty
    totalCost = totalCost.toString();

    // call the contract from the user's current address (this is just test code)
    // https://docs.ethers.io/v5/api/utils/transactions/
    // https://stackoverflow.com/questions/68198724/how-would-i-send-an-eth-value-to-specific-smart-contract-function-that-is-payabl
    CONTRACT.mintNFTs(2, {value: ethers.utils.parseEther(totalCost), gasLimit: GAS_LIMIT, type: TRANSACTION_TYPE}).then(function (transactionResponse) {
        // wait for the event to respond
        transactionResponse.wait(CONFIRMED_BLOCKS).then(function (transactionReceipt) {
            alert("Congratulations on your purchase of " + amount + "Avvenire Citizens!");

        });

    });
}

async function load_document()
{
    // wait until you are connected
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    let currentBlock = await provider.getBlockNumber();

    // get the mint price --> sets global variable
    await getMintPrice();

    // if the mint start time is past the current time, enable the button
    CONTRACT.saleConfig().then(function (resp) {
        if (resp[0] < Date.now())
        {
            // enable the button
            $('#mint-btn').attr('class', 'btn more-btn');
        }
    });

    // set the price
    $('#price').text(PRICE);

    setTotalCost();
}


// function to change the value of the total cost tag when the input box is changed
$('#amount').on('change', function () {
    setTotalCost();
});


// load the document
load_document();

// listen for event: https://docs.ethers.io/v5/api/contract/contract/#Contract--events

/*
NOTES
- where should we allow the user to set the gas limit?
- what should we do on a transaction success?
- what should we do on a transaction failure?
*/

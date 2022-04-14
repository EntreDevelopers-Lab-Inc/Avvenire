// need to verify with metamask: https://docs.metamask.io/guide/registering-function-names.html

// get some constants
var PRICE;


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
        // if in the future, get the start price
        if (parseFloat(ethers.utils.formatEther(config[0])) > Date.now())
        {
            CONTRACT.AUCTION_START_PRICE().then(
                function (resp) {
                    price = resp;
                });
        }
        // else, get the auction price
        else
        {
            CONTRACT.getAuctionPrice().then(
                function (resp) {
                    price = resp;
                });

        }

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

    // make the total cost a string for the parse ether utilty
    totalCost = totalCost.toString();

    // decide which contract to interact with
    // get the sale information
    await CONTRACT.saleConfig().then(
        function (resp) {
            config = resp;
        });

    // check if the auction is on with saleConfig.auctionSaleStartTime <= block.time_stamp
    if (parseFloat(ethers.utils.formatEther(config[0])) > 0)  // this will be set to 0 when the auction is over
    {
        // if in the future, get the start price
        if (parseFloat(ethers.utils.formatEther(config[0])) > Date.now())
        {
            CONTRACT.AUCTION_START_PRICE().then(
                function (resp) {
                    price = resp;
                });
        }
        // else, get the auction price
        else
        {
            CONTRACT.getAuctionPrice().then(
                function (resp) {
                    price = resp;
                });

        }

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


    await CONTRACT.mintNFTs(2, {value: ethers.utils.parseEther(totalCost), gasLimit: gasLimit});

    alert("Congratulations on your purchase of " + amount + "Avvenire Citizens!")
}

async function loadDocument()
{
    // wait until you are connected
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    let currentBlock = await provider.getBlockNumber();

    // get the mint price --> sets global variable
    await getMintPrice();

    // if the mint start time is past the current time and the public sale has not started yet, enable the button
    CONTRACT.saleConfig().then(function (resp) {
        if ((Date.now() > resp[0]) && (Date.now() > resp[1]))
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
loadDocument();

// listen for event: https://docs.ethers.io/v5/api/contract/contract/#Contract--events

/*
NOTES
- where should we allow the user to set the gas limit?
- what should we do on a transaction success?
- what should we do on a transaction failure?
*/

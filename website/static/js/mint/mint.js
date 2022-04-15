// need to verify with metamask: https://docs.metamask.io/guide/registering-function-names.html

// get some constants
var PRICE;

const PUBLIC_SALE_KEY = 777;


// function to get the mint price
// mint order: 1000 DA (3) --> WL (2) --> public (2000)
// this should also set the min/max/value of the input button
async function getMintPrice()
{
    // contract data
    var config;
    var price = 0;
    var whitelisted;

    // input box data
    var max;
    var value;
    var remainder;

    // get the current balance
    var userBalance = await ERC721_CONTRACT.balanceOf(window.ethereum.selectedAddress);
    var collectionSize = parseInt(ethers.utils.formatUnits(await CONTRACT.collectionSize(), 'wei'));
    var totalSupply = parseInt(ethers.utils.formatUnits(await ERC721_CONTRACT.getTotalSupply(), 'wei'));

    // mint button
    var mintBtn = $('#mint-btn');


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
        if (parseFloat(ethers.utils.formatEther(config[0])) > (Date.now() / 1000))
        {
            price = await CONTRACT.AUCTION_START_PRICE();
        }
        // else, get the auction price
        else
        {
            price = await CONTRACT.getAuctionPrice();

        }

        // set the max and value
        max = await CONTRACT.maxPerAddressDuringAuction();  // set this to the amount that can be minted (check balance of)
        value = max;

        remainder = max - userBalance;
    }
    // check if the user is whitelisted and the price is greater than 0
    else if ((parseFloat(ethers.utils.formatEther(config[2])) > 0) && (config[1] > (Date.now() / 1000)))
    {
        if (whitelisted)
        {
            // if the user is whitelisted saleConfig.mintlistPrice
            price = config[2];

            max = await CONTRACT.maxPerAddressDuringWhiteList();
            value = max;

            remainder = (max + (await CONTRACT.maxPerAddressDuringAuction())) - userBalance;
        }
        else
        {
            mintBtn.text('Minting Whitelist...');
            $('#mint-btn').attr('class', 'btn more-btn disabled');
            $('#mint-info').hide();
        }
    }
    // else, use the public sale price by calling saleConfig.publicPrice
    else if (totalSupply < collectionSize)
    {
        price = config[3];

        max = 2000;
        value = 5;
    }
    else
    {
        // make the default case that is is not mintable --> remove everything, change the mint buton's text to SOLD OUT
        $('#mint-info').hide();

        mintBtn.text('SOLD OUT');

        $('#mint-btn').attr('class', 'btn more-btn disabled');
    }

    // only set everything if the price is more than 0
    if (price > 0)
    {
        // if balance of is greater than or equal to max, diasble the mint button
        if (remainder <= 0)
        {
            $('#mint-btn').attr('class', 'btn more-btn disabled');
        }
        else if ((remainder < max) && (remainder < 5))
        {
            value = remainder;
        }

        // decrement the max
        max = remainder;

        // convert the price to eth from gwei
        price = parseFloat(ethers.utils.formatEther(price));

        // change the max and value
        $('#amount').attr('max', max);
        $('#amount').val(value);

        // set the global variable
        PRICE = price;
    }

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
    var totalCost = ethers.utils.parseEther($('#total-cost').text().toString());

    // check if the user is whitelisted
    var whitelisted;
    await CONTRACT.allowlist(window.ethereum.selectedAddress).then(function (resp) {
        // set whether this address is whitelisted
        whitelisted = ethers.utils.formatUnits(resp) != 0;
    });

    // keep track of the transaction
    var txn;

    // decide which contract to interact with
    // get the sale information
    await CONTRACT.saleConfig().then(
        function (resp) {
            config = resp;
        });

    // check if the auction is on with saleConfig.auctionSaleStartTime <= block.time_stamp
    if (parseFloat(ethers.utils.formatEther(config[0])) > 0)  // this will be set to 0 when the auction is over
    {
        // mint using the auction
        txn = CONTRACT.auctionMint(amount, {value: totalCost});
    }
    // check if the user is whitelisted and the price is greater than 0
    else if ((parseFloat(ethers.utils.formatEther(config[2])) > 0) && (config[1] > (Date.now() / 1000)))
    {
        // whitelist mint
        txn = CONTRACT.whiteListMint(amount, {value: totalCost});
    }
    // else, use the public sale price by calling saleConfig.publicPrice
    else
    {
        // public sale mint
        txn = CONTRACT.publicSaleMint(amount, PUBLIC_SALE_KEY, {value: totalCost});
    }

    // on the transaction, do different things
    txn.then(function (resp) {

        // wait for the confirmed blocks
        resp.wait(CONFIRMED_BLOCKS).then(function (receipt) {
            // alert that the mint went through
            alert("Congratulations on your purchase of " + amount + " Avvenire Citizens!")
            location.href = '/mint';
        });

    }).catch((error) => {
        // send whatever error happened
        alert('Error on mint: ' + error.message);
    });

}

async function loadDocument()
{
    // wait until you are connected
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    let currentBlock = await provider.getBlockNumber();

    // if there is no selected address, reroute to home
    if (window.ethereum.selectedAddress == null)
    {
        location.href = '/';
    }

    // get the mint price --> sets global variable
    await getMintPrice();

    // if the mint start time is past the current time and the public sale has not started yet, enable the button
    CONTRACT.saleConfig().then(function (resp) {
        if (((Date.now() / 1000) > resp[0]) && ((Date.now() / 1000) > resp[1]))
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

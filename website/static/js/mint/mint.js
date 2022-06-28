// need to verify with metamask: https://docs.metamask.io/guide/registering-function-names.html

// get some constants
var PRICE;
var CURRENT_ACCOUNT;
var LIMIT = 100;

const PUBLIC_SALE_KEY = 777;


// function to get the mint price
// mint order: DA --> WL --> public
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
    var userBalance = await ERC721_CONTRACT.balanceOf(CURRENT_ACCOUNT);
    var collectionSize = parseInt(ethers.utils.formatUnits(await CONTRACT.collectionSize(), 'wei'));
    var totalSupply = parseInt(ethers.utils.formatUnits(await ERC721_CONTRACT.getTotalSupply(), 'wei'));

    // mint button
    var mintBtn = $('#mint-btn');

    // whitelisted
    var whitelisted = false;

    // get the sale information
    await CONTRACT.saleConfig().then(
        function (resp) {
            config = resp;
        });

    // get the supply
    var totalSupply = parseInt(await ERC721_CONTRACT.getTotalSupply());

    // check if the auction is on with saleConfig.auctionSaleStartTime <= block.time_stamp
    if (totalSupply < collectionSize)
    {
        price = config[3];

        if (Date.now() < 1656453639395)
        {
            console.log('in if statement')
            // get the whitelist information
            await fetch('https://avvenire.io/wl_exists/' + CURRENT_ACCOUNT).then(function(raw) {
                return raw.json();
            }).then(
                function (resp) {
                    whitelisted = resp.exists;
                    limit = resp.limit;
                    console.log(resp);
            }).catch(function() {
                alert('Error in getting WL info. Please reload the page.')
                return;
            });
        }
        else
        {
            whitelisted = true;
            limit = 5;
        }


        // if balance of account is > limit, set price to 0 (disallows mint)
        if ((whitelisted) && (userBalance >= limit))
        {
            $('#mint-info').hide();
            mintBtn.text('Minted Max');
            $('#mint-btn').attr('class', 'btn more-btn disabled');
            price = 0;
            LIMIT = 0;
        }
        else if (whitelisted)
        {
            // set the max and min
            max = limit - userBalance;
            value = max;
            LIMIT = max;
        }
        else
        {
            $('#mint-info').hide();
            mintBtn.text('WL Mint Only');
            $('#mint-btn').attr('class', 'btn more-btn disabled');
            price = 0;
            LIMIT = 0;
        }

    }
    else if (totalSupply >= 5000)
    {
        // make the default case that is is not mintable --> remove everything, change the mint buton's text to SOLD OUT
        $('#mint-info').hide();

        mintBtn.text('SOLD OUT');

        $('#mint-btn').attr('class', 'btn more-btn disabled');
    }

    // only set everything if the price is more than 0
    if (price > 0)
    {
        // if balance of is greater than or equal to max, disable the mint button
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

        // enable the button
        $('#mint-btn').attr('class', 'btn more-btn');

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
    $('#total-cost').text((Math.ceil(PRICE * amount * 100000) / 100000).toFixed(5));
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
async function mintNFTs() {
    // set loading to true
    $('#loading').attr('hidden',
        false);
    $('#mint-btn').attr('hidden', true);

    // get the amount from the input box
    var amount = $('#amount').val();

    // make the total cost a string for the parse ether utilty
    var totalCost = ethers.utils.parseEther($('#total-cost').text().toString());

    // check if the user is whitelisted
    var whitelisted;
    await CONTRACT.allowlist(CURRENT_ACCOUNT).then(function (resp) {
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
        if (amount > LIMIT)
        {
            amount = LIMIT;
            alert('You cannot mint more than ' + LIMIT + ' citizens.');

            // set loading to false
            $('#loading').attr('hidden',
                true);
            $('#mint-btn').attr('hidden', false);

            return;
        }

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

            // set loading to false
            $('#loading').attr('hidden',
                true);
            $('#mint-btn').attr('hidden', false);
        });

    }).catch((error) => {
        // send whatever error happened
        alert('Error on mint: ' + error.message);

        // set loading to false
            $('#loading').attr('hidden',
                true);
            $('#mint-btn').attr('hidden', false);
    });

}

async function loadDocument()
{
    // wait until you are connected
    // const provider = new ethers.providers.Web3Provider(window.ethereum);
    let currentBlock = await provider.getBlockNumber();

    // get the mint price --> sets global variable
    await getMintPrice();

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


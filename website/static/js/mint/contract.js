const GWEI_PER_ETH = 1000000000;

// set the gas limit
const GAS_LIMIT = 100000

// contract provider https://github.com/mikec3/my_tutorials/blob/master/simple_storage/src/SimpleStorage.js
let CONTRACT_PROVIDER = new ethers.providers.Web3Provider(window.ethereum, network=CHAIN_STRING);

// set the transaction type
// 0 is for legacy, but metamask defaults to 2 (which is EIP-1559)
const TRANSACTION_TYPE = 2;

// contract address with (currently a test one)
const CONTRACT_ADDRESS = '0xb06cb5c94c1f71761ff6cc8d6c405ec6e70b9836';

// contract interface
const CONTRACT_ABI = [
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "maxPerAddressDuringAuction_",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "maxPerAddressDuringWhiteList_",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "collectionSize_",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "amountForAuctionAndTeam_",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "amountForTeam_",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "devAddress_",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "paymentToDevs_",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "avvenireCitizensContractAddress_",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "previousOwner",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "newOwner",
          "type": "address"
        }
      ],
      "name": "OwnershipTransferred",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "AUCTION_DROP_INTERVAL",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "AUCTION_DROP_PER_STEP",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "AUCTION_END_PRICE",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "AUCTION_PRICE_CURVE_LENGTH",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "AUCTION_START_PRICE",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "allowlist",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "amountForAuctionAndTeam",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "amountForTeam",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "quantity",
          "type": "uint256"
        }
      ],
      "name": "auctionMint",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "collectionSize",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint64",
          "name": "mintlistPriceWei",
          "type": "uint64"
        },
        {
          "internalType": "uint64",
          "name": "publicPriceWei",
          "type": "uint64"
        },
        {
          "internalType": "uint32",
          "name": "publicSaleStartTime",
          "type": "uint32"
        }
      ],
      "name": "endAuctionAndSetupNonAuctionSaleInfo",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAuctionPrice",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "publicPriceWei",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "publicSaleKey",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "publicSaleStartTime",
          "type": "uint256"
        }
      ],
      "name": "isPublicSaleOn",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "maxPerAddressDuringAuction",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "maxPerAddressDuringWhiteList",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "quantity",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "callerPublicSaleKey",
          "type": "uint256"
        }
      ],
      "name": "publicSaleMint",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "toRefund",
          "type": "address"
        }
      ],
      "name": "refund",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "refundMe",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "toRemove",
          "type": "address"
        }
      ],
      "name": "removeFromWhitelist",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "renounceOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "saleConfig",
      "outputs": [
        {
          "internalType": "uint32",
          "name": "auctionSaleStartTime",
          "type": "uint32"
        },
        {
          "internalType": "uint32",
          "name": "publicSaleStartTime",
          "type": "uint32"
        },
        {
          "internalType": "uint64",
          "name": "mintlistPrice",
          "type": "uint64"
        },
        {
          "internalType": "uint64",
          "name": "publicPrice",
          "type": "uint64"
        },
        {
          "internalType": "uint32",
          "name": "publicSaleKey",
          "type": "uint32"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address[]",
          "name": "addresses",
          "type": "address[]"
        }
      ],
      "name": "seedWhitelist",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint32",
          "name": "timestamp",
          "type": "uint32"
        }
      ],
      "name": "setAuctionSaleStartTime",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint32",
          "name": "key",
          "type": "uint32"
        }
      ],
      "name": "setPublicSaleKey",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "teamMint",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "totalPaid",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "newOwner",
          "type": "address"
        }
      ],
      "name": "transferOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "quantity",
          "type": "uint256"
        }
      ],
      "name": "whiteListMint",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "withdrawMoney",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

// get the signer
let SIGNER = CONTRACT_PROVIDER.getSigner();

// make contract
let CONTRACT = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, SIGNER);

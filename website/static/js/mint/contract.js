const GWEI_PER_ETH = 1000000000;

// set the transaction type
// 0 is for legacy, but metamask defaults to 2 (which is EIP-1559)
const TRANSACTION_TYPE = 2;

// contract address with (currently a test one)
const CONTRACT_ADDRESS = '0x7bF109cEa662AC66b07c189c2fc8F1cE909ad350';
const ERC721_CONTRACT_ADDR = '0x42Ef5eb48586757b2F69A37569B6F35120f2515e';

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

const ERC721_ABI = [
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "ERC721Name_",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "ERC721AId_",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "baseURI_",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "loadURI_",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "devAddress_",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "dataContractAddress_",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [],
      "name": "AllOwnershipsHaveBeenSet",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "ApprovalCallerNotOwnerNorApproved",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "ApprovalQueryForNonexistentToken",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "ApprovalToCurrentOwner",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "ApproveToCaller",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "BalanceQueryForZeroAddress",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "ChangeAlreadyRequested",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "InsufficcientFunds",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "MintToZeroAddress",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "MintZeroQuantity",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "NoTokensMintedYet",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "NotSender",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "OwnerQueryForNonexistentToken",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "QuantityMustBeNonZero",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "TraitTypeDoesNotExist",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "TransferCallerNotOwnerNorApproved",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "TransferFromIncorrectOwner",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "TransferToNonERC721ReceiverImplementer",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "TransferToZeroAddress",
      "type": "error"
    },
    {
      "inputs": [],
      "name": "URIQueryForNonexistentToken",
      "type": "error"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "approved",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "Approval",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "operator",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "bool",
          "name": "approved",
          "type": "bool"
        }
      ],
      "name": "ApprovalForAll",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "contractAddress",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "sender",
          "type": "address"
        }
      ],
      "name": "ChangeRequested",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "bool",
          "name": "configuration",
          "type": "bool"
        }
      ],
      "name": "CitizenMintActivityConfigured",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "configuration",
          "type": "uint256"
        }
      ],
      "name": "MutabilityCostConfigured",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "bool",
          "name": "configuration",
          "type": "bool"
        }
      ],
      "name": "MutabilityModeConfigured",
      "type": "event"
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
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "citizenId",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "traitId",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "enum AvvenireCitizenDataInterface.TraitType",
          "name": "traitType",
          "type": "uint8"
        }
      ],
      "name": "TraitBound",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "TraitNonTransferrable",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "TraitTransferrable",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "Transfer",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "approve",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "avvenireCitizensData",
      "outputs": [
        {
          "internalType": "contract AvvenireCitizensMappingsInterface",
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
          "internalType": "address",
          "name": "owner",
          "type": "address"
        }
      ],
      "name": "balanceOf",
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
          "name": "citizenId",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "traitId",
          "type": "uint256"
        },
        {
          "internalType": "enum AvvenireCitizenDataInterface.Sex",
          "name": "sex",
          "type": "uint8"
        },
        {
          "internalType": "enum AvvenireCitizenDataInterface.TraitType",
          "name": "traitType",
          "type": "uint8"
        }
      ],
      "name": "bind",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "burn",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "devAddress_",
          "type": "address"
        }
      ],
      "name": "changeDevAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "citizenMintActive",
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
      "inputs": [
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "getApproved",
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
      "inputs": [],
      "name": "getChangeCost",
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
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "getCitizen",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "tokenId",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "uri",
              "type": "string"
            },
            {
              "internalType": "bool",
              "name": "exists",
              "type": "bool"
            },
            {
              "internalType": "enum AvvenireCitizenDataInterface.Sex",
              "name": "sex",
              "type": "uint8"
            },
            {
              "components": [
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "background",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "body",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "tattoo",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "eyes",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "mouth",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "mask",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "necklace",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "clothing",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "earrings",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "hair",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "effect",
                  "type": "tuple"
                }
              ],
              "internalType": "struct AvvenireCitizenDataInterface.Traits",
              "name": "traits",
              "type": "tuple"
            }
          ],
          "internalType": "struct AvvenireCitizenDataInterface.Citizen",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getCitizenMintActive",
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
      "name": "getMutabilityConfig",
      "outputs": [
        {
          "components": [
            {
              "internalType": "bool",
              "name": "mutabilityMode",
              "type": "bool"
            },
            {
              "internalType": "uint256",
              "name": "mutabilityCost",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "tradeBeforeChange",
              "type": "bool"
            }
          ],
          "internalType": "struct AvvenireCitizensInterface.MutabilityConfig",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getMutabilityMode",
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
      "inputs": [
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "getOwnershipData",
      "outputs": [
        {
          "components": [
            {
              "internalType": "address",
              "name": "addr",
              "type": "address"
            },
            {
              "internalType": "uint64",
              "name": "startTimestamp",
              "type": "uint64"
            },
            {
              "internalType": "bool",
              "name": "burned",
              "type": "bool"
            }
          ],
          "internalType": "struct ERC721A.TokenOwnership",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getTotalSupply",
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
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "getTrait",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "tokenId",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "uri",
              "type": "string"
            },
            {
              "internalType": "bool",
              "name": "free",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "exists",
              "type": "bool"
            },
            {
              "internalType": "enum AvvenireCitizenDataInterface.Sex",
              "name": "sex",
              "type": "uint8"
            },
            {
              "internalType": "enum AvvenireCitizenDataInterface.TraitType",
              "name": "traitType",
              "type": "uint8"
            },
            {
              "internalType": "uint256",
              "name": "originCitizenId",
              "type": "uint256"
            }
          ],
          "internalType": "struct AvvenireCitizenDataInterface.Trait",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "operator",
          "type": "address"
        }
      ],
      "name": "isApprovedForAll",
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
      "name": "loadURI",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "mutabilityConfig",
      "outputs": [
        {
          "internalType": "bool",
          "name": "mutabilityMode",
          "type": "bool"
        },
        {
          "internalType": "uint256",
          "name": "mutabilityCost",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "tradeBeforeChange",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "name",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "nextOwnerToExplicitlySet",
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
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "numberBurned",
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
          "name": "owner",
          "type": "address"
        }
      ],
      "name": "numberMinted",
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
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "ownerOf",
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
      "inputs": [],
      "name": "renounceOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "requestChange",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "address_",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "quantity_",
          "type": "uint256"
        }
      ],
      "name": "safeMint",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "safeTransferFrom",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        },
        {
          "internalType": "bytes",
          "name": "_data",
          "type": "bytes"
        }
      ],
      "name": "safeTransferFrom",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "address_",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "setting",
          "type": "bool"
        }
      ],
      "name": "setAllowedPermission",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "operator",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "approved",
          "type": "bool"
        }
      ],
      "name": "setApprovalForAll",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "baseURI_",
          "type": "string"
        }
      ],
      "name": "setBaseURI",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "tokenId",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "uri",
              "type": "string"
            },
            {
              "internalType": "bool",
              "name": "exists",
              "type": "bool"
            },
            {
              "internalType": "enum AvvenireCitizenDataInterface.Sex",
              "name": "sex",
              "type": "uint8"
            },
            {
              "components": [
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "background",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "body",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "tattoo",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "eyes",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "mouth",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "mask",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "necklace",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "clothing",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "earrings",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "hair",
                  "type": "tuple"
                },
                {
                  "components": [
                    {
                      "internalType": "uint256",
                      "name": "tokenId",
                      "type": "uint256"
                    },
                    {
                      "internalType": "string",
                      "name": "uri",
                      "type": "string"
                    },
                    {
                      "internalType": "bool",
                      "name": "free",
                      "type": "bool"
                    },
                    {
                      "internalType": "bool",
                      "name": "exists",
                      "type": "bool"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.Sex",
                      "name": "sex",
                      "type": "uint8"
                    },
                    {
                      "internalType": "enum AvvenireCitizenDataInterface.TraitType",
                      "name": "traitType",
                      "type": "uint8"
                    },
                    {
                      "internalType": "uint256",
                      "name": "originCitizenId",
                      "type": "uint256"
                    }
                  ],
                  "internalType": "struct AvvenireCitizenDataInterface.Trait",
                  "name": "effect",
                  "type": "tuple"
                }
              ],
              "internalType": "struct AvvenireCitizenDataInterface.Traits",
              "name": "traits",
              "type": "tuple"
            }
          ],
          "internalType": "struct AvvenireCitizenDataInterface.Citizen",
          "name": "citizen",
          "type": "tuple"
        },
        {
          "internalType": "bool",
          "name": "changeUpdate",
          "type": "bool"
        }
      ],
      "name": "setCitizenData",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bool",
          "name": "citizenMintActive_",
          "type": "bool"
        }
      ],
      "name": "setCitizenMintActive",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "devRoyaltyPercent_",
          "type": "uint256"
        }
      ],
      "name": "setDevRoyalty",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bool",
          "name": "_isStopped",
          "type": "bool"
        }
      ],
      "name": "setEmergencyStop",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "loadURI_",
          "type": "string"
        }
      ],
      "name": "setLoadURI",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "mutabilityCost_",
          "type": "uint256"
        }
      ],
      "name": "setMutabilityCost",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bool",
          "name": "mutabilityMode_",
          "type": "bool"
        }
      ],
      "name": "setMutabilityMode",
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
      "name": "setOwnersExplicit",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "receivingAddress_",
          "type": "address"
        }
      ],
      "name": "setReceivingAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bool",
          "name": "setting",
          "type": "bool"
        }
      ],
      "name": "setTokenTradeBeforeChange",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "tokenId",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "uri",
              "type": "string"
            },
            {
              "internalType": "bool",
              "name": "free",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "exists",
              "type": "bool"
            },
            {
              "internalType": "enum AvvenireCitizenDataInterface.Sex",
              "name": "sex",
              "type": "uint8"
            },
            {
              "internalType": "enum AvvenireCitizenDataInterface.TraitType",
              "name": "traitType",
              "type": "uint8"
            },
            {
              "internalType": "uint256",
              "name": "originCitizenId",
              "type": "uint256"
            }
          ],
          "internalType": "struct AvvenireCitizenDataInterface.Trait",
          "name": "trait",
          "type": "tuple"
        },
        {
          "internalType": "bool",
          "name": "changeUpdate",
          "type": "bool"
        }
      ],
      "name": "setTraitData",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes4",
          "name": "interfaceId",
          "type": "bytes4"
        }
      ],
      "name": "supportsInterface",
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
      "name": "symbol",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "tokenURI",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "totalSupply",
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
          "name": "from",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "tokenId",
          "type": "uint256"
        }
      ],
      "name": "transferFrom",
      "outputs": [],
      "stateMutability": "nonpayable",
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
      "inputs": [],
      "name": "withdrawMoney",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ];


// get the signer
let SIGNER = provider.getSigner();

// make contract
let CONTRACT = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, SIGNER);

// get the ERC721 contract
let ERC721_CONTRACT = new ethers.Contract(ERC721_CONTRACT_ADDR, ERC721_ABI, SIGNER);

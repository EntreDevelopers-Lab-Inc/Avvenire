// SPDX-License-Identifier: MIT

/**
 * @title token mutating contract for ERC721A
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chiru-labs/contracts/ERC721A.sol";
// _setOwnersExplicit( ) moved from the ERC721A contract to an extension
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

error TraitTypeDoesNotExist();

// token mutator changes the way that an ERC721A contract interacts with tokens
contract AvvenireCitizens is
    Ownable,
    ERC721A,
    ERC721AOwnersExplicit,
    ReentrancyGuard,
    AvvenireCitizensInterface
{
    // mint information (whether or not the platform is minting citizens)
    bool public citizenMintActive; // this defaults to true, as the platform needs to mint citizens before allowing tradable traits

    string baseURI; // a uri for minting, but this allows the contract owner to change it later
    string public loadURI; // a URI that the NFT will be set to while waiting for changes

    address payable receivingAddress; // the address that collects the cost of the mutation

    struct MutabilityConfig {
        bool mutabilityMode; // initially set the contract to be immutable, this will keep people from trying to use the function before it is released
        // payment information
        uint256 mutabilityCost; // the amount that it costs to make a change (initializes to 0)
        // trading information
        bool tradeBeforeChange; // initially set to false, don't want people to tokens that are pending changes
    }

    MutabilityConfig public mutabilityConfig;

    // dev payment
    struct DevConfig {
        address devAddress;
        uint256 devRoyaltyPercent;
    }

    DevConfig devConfig; // need to set it this way to avoid stack being too deep

    // struct for storing change information
    // want to keep this in a struct, as it will allow other contracts to add data about the change to it
    struct ChangeRequest {
        bool changeRequested;
    }

    // mapping for tokenId to citizen
    mapping(uint256 => Citizen) public tokenIdToCitizen;

    // mapping for tokenId to trait
    mapping(uint256 => Trait) public tokenIdToTrait;

    // mapping of tokenId to change request for information --> being public allows anyone to see if the changes are requested
    mapping(uint256 => ChangeRequest) public tokenChangeRequests;

    // mapping for allowing other contracts to interact with this one
    mapping(address => bool) public allowedContracts;

    // Designated # of citizens; **** Needs to be set to immutable following testings ****
    constructor(
        string memory ERC721Name_,
        string memory ERC721AId_,
        string memory baseURI_,
        string memory loadURI_,
        address devAddress_
    ) ERC721A(ERC721Name_, ERC721AId_) {
        // set the mint URI
        baseURI = baseURI_;

        // set the load uri
        loadURI = loadURI_;

        // set the receiving address to the publisher of this contract
        receivingAddress = payable(msg.sender);

        // allow this contract to interact with itself
        allowedContracts[msg.sender] = true;

        // Set mint to true
        citizenMintActive = true;

        // set the dev address for royalties and payment
        devConfig.devAddress = devAddress_;
    }

    /**
      Modifier to check if the contract is allowed to call this contract
    */
    modifier callerIsAllowed() {
        require(
            allowedContracts[msg.sender],
            "Not allowed to interact"
        );
        _;
    }

    /**
     * @notice returns the tokenURI of a token id (overrides ERC721 function)
     * @param tokenId allows the user to request the tokenURI for a particular token id
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory)
    {
        // check to make sure that the tokenId exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken(); // error from ERC721A

        // if a change has been requested, only show the loading URI
        if (tokenChangeRequests[tokenId].changeRequested) {
            return loadURI;
        }

        // if there is a citizen associated with this token, return the chacter's uri
        if (bytes(tokenIdToCitizen[tokenId].uri).length > 0) {
            return tokenIdToCitizen[tokenId].uri;
        }

        if (bytes(tokenIdToTrait[tokenId].uri).length > 0) {
            return tokenIdToTrait[tokenId].uri;
        }

        // if there is no load uri, citizen uri, or trait uri, just return the base
        return string(abi.encodePacked(baseURI, Strings.toString(tokenId)));
    }

    /** @notice a function that gives the change cost
    */
    function getChangeCost() public view returns(uint256)
    {
        return (mutabilityConfig.mutabilityCost * ((100 + devConfig.devRoyaltyPercent) / 100));
    }

    /**
     * @notice Requests a change for a token
     * @param tokenId allows the user to request a change using their token id
     */
    function requestChange(uint256 tokenId) external payable callerIsAllowed {
        // check if you can even request changes at the moment
        require(
            mutabilityConfig.mutabilityMode,
            "Tokens are currently immutable."
        );

        // check if the token exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();

        // check that this is the rightful token owner
        require(
            ownerOf(tokenId) == tx.origin,
            "Only the owner of a token can request its change."
        );

        // check if the token has already been requested to change
        require(
            !tokenChangeRequests[tokenId].changeRequested,
            "A change has already been requested for this token"
        );

        _requestChange(tokenId); // call the internal function
    }

    function _requestChange(uint256 tokenId) internal {
        // take some payment for this transaction if there is some cost set
        if (mutabilityConfig.mutabilityCost > 0) {
            // cannot require that the amount due is paid, as this function is used in when minting traits from safe mint
                // even making safeMint payable would be useless, as this can only check the value of one trait, not many
                // seems nonsensical to make safemint payable with require statements, as only allowed contracts can call it, and we would be checking ourselves at the cost of users (when we could instead write one require statement at the end of a transaction in an allowed contract)

            (bool success, ) = receivingAddress.call{
                value: mutabilityConfig.mutabilityCost
            }("");

            (bool royaltyPaid, ) = devConfig.devAddress.call{
                value: ((mutabilityConfig.mutabilityCost *
                    devConfig.devRoyaltyPercent) / 100)
            }("");

            require(success && royaltyPaid, "Wallet failed to change tokens.");
        }

        // set the token as requested to change (don't change the URI, it's a waste of gas --> will be done once in when the admin sets the token uri)
        tokenChangeRequests[tokenId].changeRequested = true;
    }

    /**
     * @notice Set the citizen data (id, uri, any traits). This will likely happen when combining nfts by the USER --> the URI should be set somewhere else, so the admin incurs minimal gas costs
     * @param citizen allows a contract to set the citizen's data to new information
     * @param changeUpdate sets the change data to the correct boolean (allows the option to set the changes to false after something has been updated OR keep it at true if the update isn't done)
     */
    function setCitizenData(Citizen memory citizen, bool changeUpdate)
        external
        callerIsAllowed
    {
        // set the citizen data
        tokenIdToCitizen[citizen.tokenId] = citizen;

        // set the token change data
        tokenChangeRequests[citizen.tokenId].changeRequested = changeUpdate;
    }

    /**
     * @notice set the trait data (id, uri, any traits)
     * @param trait allows a contract to set the trait's data to new information
     * @param changeUpdate sets the change data to the correct boolean (allows the option to set the changes to false after something has been updated OR keep it at true if the update isn't done)
     */
    function setTraitData(Trait memory trait, bool changeUpdate)
        external
        callerIsAllowed
    {
        // set the trait data
        tokenIdToTrait[trait.tokenId] = trait;

        // set the token change data
        tokenChangeRequests[trait.tokenId].changeRequested = changeUpdate;
    }

    /**
     * @notice Sets the mutability of the contract (whether changes are accepted)
     * @param mutabilityMode_ allows the contract owner to change the mutability of the tokens
     */
    function setMutablityMode(bool mutabilityMode_) external onlyOwner {
        // set te new mutability mode to this boolean
        mutabilityConfig.mutabilityMode = mutabilityMode_;
    }

    /**
     * @notice gets the mutability of a contract
     */
    function getMutabilityMode() public view returns (bool) {
        return mutabilityConfig.mutabilityMode;
    }

    /**
     * @notice Sets the mint uri
     * @param baseURI_ represents the new base uri
     */
    function setBaseURI(string calldata baseURI_) external onlyOwner {
        // set thte global baseURI to this new baseURI_
        baseURI = baseURI_;
    }

    /**
     * @notice Sets the load uri
     * @param loadURI_ represents the new load uri
     */
    function setLoadURI(string calldata loadURI_) external onlyOwner {
        // set thte global loadURI to this new loadURI_
        loadURI = loadURI_;
    }

    /**
     * @notice a function to toggle the citizen mint
     * @param citizenMintActive_ as the boolean setting
     */
    function setCitizenMintActive(bool citizenMintActive_) external onlyOwner {
        citizenMintActive = citizenMintActive_;
    }

    /**
     * @notice a function to get the citizen mint information
     */
    function getCitizenMintActive() public view returns (bool) {
        return citizenMintActive;
    }

    /**
     * @notice Sets the mutability cost
     * @param mutabilityCost_ is the new mutability cost
     */
    function setMutabilityCost(uint256 mutabilityCost_) external onlyOwner {
        mutabilityConfig.mutabilityCost = mutabilityCost_;
    }

    /**
     * @notice Sets the receivingAddress
     * @param receivingAddress_ is the new receiving address
     */
    function setReceivingAddress(address receivingAddress_) external onlyOwner {
        receivingAddress = payable(receivingAddress_);
    }

    /**
     * @notice allow the devs to change their address
     * @param devAddress_ would be the new dev address
     */
    function changeDevAddress(address devAddress_) external {
        require(
            msg.sender == devConfig.devAddress,
            "Only the devs can change their address."
        );

        devConfig.devAddress = devAddress_;
    }

    /**
     * @notice allow the devs to set their royalties
     * @param devRoyaltyPercent_ is the percent (out of 100) to pay the devs
     */
    function setDevRoyalty(uint256 devRoyaltyPercent_) external {
        require(
            msg.sender == devConfig.devAddress,
            "Only the devs can change their royalty."
        );

        devConfig.devRoyaltyPercent = devRoyaltyPercent_;
    }

    /**
     * @notice set whether or not the token can be traded while changes are pending
     * @param setting is a boolean of the change
     */
    function setTokenTradeBeforeChange(bool setting) external onlyOwner {
        mutabilityConfig.tradeBeforeChange = setting;
    }

    /**
     * @notice sets an address's allowed list permission (for future interaction)
     * @param address_ is the address to set the data for
     * @param setting is the boolean for the data
     */
    function setAllowedPermission(address address_, bool setting)
        external
        onlyOwner
    {
        allowedContracts[address_] = setting;
    }

    /**
     * @notice internal function for getting the default trait (mostly for creating new citizens, waste of compute for creating new traits)
     */
    function baseTrait(Sex sex, TraitType traitType)
        internal
        returns (Trait memory)
    {
        return
            Trait({
                tokenId: 0, // there will be no traits with tokenId 0, as that must be the first citizen (cannot have traits without minting the first citizen)
                uri: "",
                free: false,
                exists: true,
                sex: sex,
                traitType: traitType
            });
    }

    /**
     * @notice internal function to create a new citizen
     * @param tokenId (for binding the token id)
     */
    function createNewCitizen(uint256 tokenId) internal {
        // create a new citizen and put it in the mapping --> just set the token id and that it exists, don't set any of the traits or the URI (as these can be handled in the initial mint)
        tokenIdToCitizen[tokenId] = Citizen({
            tokenId: tokenId,
            uri: "", // keep this blank to keep the user from paying excess gas before decomposition (the tokenURI function will handle for blank URIs)
            exists: true,
            sex: Sex.NULL,
            traits: Traits({
                background: baseTrait(Sex.NULL, TraitType.BACKGROUND),
                body: baseTrait(Sex.NULL, TraitType.BODY),
                tattoo: baseTrait(Sex.NULL, TraitType.TATTOO),
                eyes: baseTrait(Sex.NULL, TraitType.EYES),
                mouth: baseTrait(Sex.NULL, TraitType.MOUTH),
                mask: baseTrait(Sex.NULL, TraitType.MASK),
                necklace: baseTrait(Sex.NULL, TraitType.NECKLACE),
                clothing: baseTrait(Sex.NULL, TraitType.CLOTHING),
                earrings: baseTrait(Sex.NULL, TraitType.EARRINGS),
                hair: baseTrait(Sex.NULL, TraitType.HAIR),
                effect: baseTrait(Sex.NULL, TraitType.EFFECT)
            })
        });
    }

    /**
     * @notice internal function to create a new trait (called after token transfer --> in safe mint)
     * @param tokenId (for binding the token id)
     */
    function createNewTrait(uint256 tokenId) internal {
        // create a new trait and put it in the mapping --> just set the token id, that it exists and that it is free
        tokenIdToTrait[tokenId] = Trait({
            tokenId: tokenId,
            uri: "",
            free: true,
            exists: true,
            sex: Sex.NULL,
            traitType: TraitType.NULL
        });

        // everytime a new trait is created, a change must be requested, as there is no data bound to it yet
        _requestChange(tokenId);
    }

    /**
     * @notice a function callable by another contract to set a trait back to being free
     * set to public to allow it to be called both internally and by other contracts
     * @param tokenId for the token that is being altered
     */
    function respawnTrait(uint256 tokenId) external callerIsAllowed {
        // check if the trait exists
        require(tokenIdToTrait[tokenId].exists, "This trait does not exist.");

        // check if the trait is free
        require(
            !tokenIdToTrait[tokenId].free,
            "This trait is not bound to anything."
        );

        // set the token's owner to the origin of the contract call
        // don't want this to be the message sender, as that is likely to be another contract
        // can't be the owner of, as it is not bound to anything
        _ownerships[tokenId].addr = tx.origin;

        // set the token to being free
        tokenIdToTrait[tokenId].free = true;
    }

    /**
     * @notice an internal function to get a trait for binding --> only for use within binding and unbinding (want to make it easy for the bind function to be overridden)
     * trait is guaranteed to exist, as this is only called when binding
     * @param traitId indicated the trait id that will be bound (can be set to 0 for a non-existend trait that adheres to the type)
     * @param traitType indicates the type of trait to be bound
     */
    function lockAndReturnTraitForBinding(
        uint256 traitId,
        Sex sex,
        TraitType traitType
    ) internal returns (Trait memory) {
        // store the trait that should be bound
        if (traitId == 0) {
            // this trait does not exist, just set it to the default struct
            Trait memory trait = Trait({
                tokenId: traitId,
                uri: "",
                free: false,
                exists: false,
                sex: sex,
                traitType: traitType
            });

            return trait;
        } else {
            // check the owner of the trait
            require(
                ownerOf(traitId) == tx.origin,
                "The transaction origin does not own the trait"
            );

            // the trait exists and can be found
            Trait memory trait = tokenIdToTrait[traitId];

            // require that the trait's type is the same type as the trait Id (if the user tries to put traits on the wrong parts of NFTs)
            require(
                trait.traitType == traitType,
                "Trait type does not match trait id"
            );

            // disallow trading of the bound trait
            makeTraitNonTransferrable(traitId);

            return trait;
        }
    }

    /**
     * @notice internal function to make traits transferrable (used when binding traits)
     * checks that a trait exists (makes user unable to set a default to a default)
     * @param traitId indicating which trait to set
     */
    function makeTraitTransferable(uint256 traitId) internal {
        require(tokenIdToTrait[traitId].exists, "This trait does not exist.");

        // set the ownership to the transaction origin
        _ownerships[traitId].addr = tx.origin;

        // set the trait to free (should be tradable and combinable)
        tokenIdToTrait[traitId].free = true;
    }

    /**
     * @notice internal function to make traits non-transferrable
     * checks that a trait exists (makes user unable to set a default to a default)
     * @param traitId to indicate which trait to change
     */
    function makeTraitNonTransferrable(uint256 traitId) internal {
        require(tokenIdToTrait[traitId].exists, "This trait does not exist.");

        // set the ownership to null
        _ownerships[traitId].addr = address(0);

        // set the trait to not free (should not be tradable or combinable any longer)
        tokenIdToTrait[traitId].free = false;
    }

    /**
     * @notice a function to bind a tokenId to a citizen (used in combining)
     * Note: the tokenId must exist, this does not create new tokens (use spawn traits for that)
     * going to assume that the transaction origin owns the citizen (this function will be called multiple times)
     * Also, this does not set the character up for changing. It is assumed that many traits will be bound for a character to be changed, so the character should be requested to change once.
     * @param citizenId gets the citizen
     * @param traitId for the trait
     * @param traitType for the trait's type
     */
    function bind(
        uint256 citizenId,
        uint256 traitId,
        Sex sex,
        TraitType traitType
    ) external callerIsAllowed {
        // if binding non-empty trait, must require the correct sex and ensure that the tokenId exists
        if (traitId != 0) {
            // check if the trait exists
            require(
                tokenIdToTrait[traitId].exists,
                "This trait does not exist."
            );

            // ensure that the trait and citizen have the same sex
            require(
                tokenIdToCitizen[citizenId].sex == tokenIdToTrait[traitId].sex,
                "You cannot combine traits from opposite sexes."
            );
        }

        // check each of the types and bind them accordingly
        if (traitType == TraitType.BACKGROUND) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.background.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .background = lockAndReturnTraitForBinding(
                traitId,
                sex,
                traitType
            );
        } else if (traitType == TraitType.BODY) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.body.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .body = lockAndReturnTraitForBinding(traitId, sex, traitType);
        } else if (traitType == TraitType.TATTOO) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.tattoo.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .tattoo = lockAndReturnTraitForBinding(traitId, sex, traitType);
        } else if (traitType == TraitType.EYES) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.eyes.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .eyes = lockAndReturnTraitForBinding(traitId, sex, traitType);
        } else if (traitType == TraitType.MOUTH) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.mouth.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .mouth = lockAndReturnTraitForBinding(traitId, sex, traitType);
        } else if (traitType == TraitType.MASK) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.mask.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .mask = lockAndReturnTraitForBinding(traitId, sex, traitType);
        } else if (traitType == TraitType.NECKLACE) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.necklace.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .necklace = lockAndReturnTraitForBinding(
                traitId,
                sex,
                traitType
            );
        } else if (traitType == TraitType.CLOTHING) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.clothing.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .clothing = lockAndReturnTraitForBinding(
                traitId,
                sex,
                traitType
            );
        } else if (traitType == TraitType.EARRINGS) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.earrings.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .earrings = lockAndReturnTraitForBinding(
                traitId,
                sex,
                traitType
            );
        } else if (traitType == TraitType.HAIR) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.hair.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .hair = lockAndReturnTraitForBinding(traitId, sex, traitType);
        } else if (traitType == TraitType.EFFECT) {
            // make the old trait transferrable
            makeTraitTransferable(
                tokenIdToCitizen[citizenId].traits.effect.tokenId
            );

            // set the new trait
            tokenIdToCitizen[citizenId]
                .traits
                .effect = lockAndReturnTraitForBinding(traitId, sex, traitType);
        } else {
            // return an error that the trait type does not exist
            revert TraitTypeDoesNotExist();
        }
    }

    /**
     * @notice external safemint function for allowed contracts
     * @param address_ for where to mint to
     * @param quantity_ for the amount
     */
    function safeMint(address address_, uint256 quantity_)
        external
        callerIsAllowed
    {
        _safeMint(address_, quantity_);
    }

    /**
     * @notice returns the number minted from specified address
     * @param owner an address of an owner in the NFT collection
     */
    function numberMinted(address owner) public view returns (uint256) {
        // check how many have been minted to this owner --> where is this data stored, in the standard?
        // _addressData mapping in the ERC721A standard; line 51 - Daniel
        return _numberMinted(owner);
    }

    /**
     * @notice Returns a struct, which contains a token owner's address and the time they acquired the token
     * @param tokenId the tokenID
     */
    function getOwnershipData(
        uint256 tokenId // storing all the old ownership
    ) external view returns (TokenOwnership memory) {
        return ownershipOf(tokenId); // get historic ownership
    }

    /**
     * @notice This overrides the token transfers to check some conditions
     * @param from indicates the previous address
     * @param to indicates the new address
     * @param startTokenId indicates the first token id
     * @param quantity shows how many tokens have been minted
     */
    function _beforeTokenTransfers(
        address from,
        address to,
        uint256 startTokenId,
        uint256 quantity
    ) internal override {
        // token id end counter
        uint256 endTokenId = startTokenId + quantity;

        // iterate over all the tokens
        for (
            uint256 tokenId = startTokenId;
            tokenId < endTokenId;
            tokenId += 1
        ) {
            // the tokens SHOULD NOT be awaiting a change (you don't want the user to get surprised)
            if (!mutabilityConfig.tradeBeforeChange) {
                require(
                    !tokenChangeRequests[tokenId].changeRequested,
                    "A change has been requested for this/these token(s)."
                );
            }

            // if this is a trait, it must be free to be transferred
            if (tokenIdToTrait[tokenId].exists) {
                require(
                    tokenIdToTrait[tokenId].free,
                    "Trait is non-transferrable."
                );
            }
        }
    }

    /**
     * @notice This overrides the after token transfers function to create structs and request changes if they are traits
     * @param from indicates the previous address
     * @param to indicates the new address
     * @param startTokenId indicates the first token id
     * @param quantity shows how many tokens have been minted
     */
    function _afterTokenTransfers(
        address from,
        address to,
        uint256 startTokenId,
        uint256 quantity
    ) internal override {
        // token id end counter
        uint256 endTokenId = startTokenId + quantity;

        // iterate over all the tokens
        for (
            uint256 tokenId = startTokenId;
            tokenId < endTokenId;
            tokenId += 1
        ) {
            // check if the token exists in the citizen or trait mapping
            if (
                (!tokenIdToCitizen[tokenId].exists) &&
                (!tokenIdToTrait[tokenId].exists)
            ) {
                // if the token id does not exist, create a new citizen or trait
                if (citizenMintActive) {
                    // create a new citizen if the mint is active
                    createNewCitizen(tokenId);
                } else {
                    // create a new trait if the citizen mint is inactive, and there is no trait mapping to the token id
                    createNewTrait(tokenId); // no way to know the trait type on token transferm so just set it to null
                }
            }
        }
    }

    /**
     * @notice gets rid of the loops used in the ownerOf function in the ERC721A standard
     * @param quantity the number of tokens that you want to eliminate the loops for
     */
    function setOwnersExplicit(uint256 quantity)
        external
        onlyOwner
        nonReentrant
    {
        _setOwnersExplicit(quantity);
    }

    /**
     * @notice function that gets the total supply from the ERC721A contract
     */
    function getTotalSupply() external view returns (uint256) {
        return totalSupply();
    }

    /**
     * @notice function to withdraw the money from the contract. Only callable by the owner
     */
    function withdrawMoney() external onlyOwner nonReentrant {
        // Withdraw rest of the contract
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "team transfer failed.");
    }
}

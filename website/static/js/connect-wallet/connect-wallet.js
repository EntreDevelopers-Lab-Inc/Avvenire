let CURRENT_ACCOUNT = null;
var provider;

// set the chain
async function setChain() {
    try {
      await provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: CHAIN_ID_STR }],
      });

    } catch (switchError) {
      // This error code indicates that the chain has not been added to MetaMask.
      if (switchError.code === 4902) {
        try {
          await provider.request({
            method: 'wallet_addEthereumChain',
            params: [
              {
                chainId: CHAIN_ID_STR,
                chainName: '...',
                rpcUrls: ['https://...'] /* ... */,
              },
            ],
          });
        } catch (addError) {
          // handle "add" error
        }
      }
      // handle other "switch" errors
    }
}

/*********************************************/
/* Access the user's accounts (per EIP-1102) */
/*********************************************/

// While you are awaiting the call to eth_requestAccounts, you should disable
// any buttons the user can click to initiate the request.
// MetaMask will reject any additional requests while the first is still
// pending.
async function connectEthereum() {
  // set the provider to ethereum
  provider = window.ethereum;

  provider
    .request({ method: 'eth_requestAccounts' })
    .then(handleAccountsChanged)
    .catch((err) => {
      if (err.code === 4001) {
        // EIP-1193 userRejectedRequest error
        // If this happens, the user rejected the connection request.
        alert('Please connect wallet.');
      } else {
        alert(err);
      }
    });

    setChain();

    // now that we are connected, hide the button
    $('#connect-btn').hide();
}

async function connectWalletConnect() {
  //  Create WalletConnect Provider
  const p = new WalletConnectProvider.default({
    chainId: CHAIN_ID_INT,
    infuraId: "27e484dcd9e3efcfd25a83a78777cdf1",
  });

  //  Enable session (triggers QR Code modal)
  await p.enable();

  // bind the provider to wallet connect
  provider = new ethers.providers.Web3Provider(p);

}


// For now, 'eth_accounts' will continue to always return an array
function handleAccountsChanged(accounts) {
  if (accounts.length === 0) {
    // MetaMask is locked or the user has not connected any accounts

    // show the connect button
    $('#connect-btn').show();

  } else if (accounts[0] !== CURRENT_ACCOUNT) {
    CURRENT_ACCOUNT = accounts[0];

    // hide the button
    $('#connect-btn').hide();
  }
}

async function handleChainChanged(_chainId) {
    await setChain();

  // We recommend reloading the page, unless you must do otherwise
  window.location.reload();
}


// make a document load function
async function loadDocument() {
    // check if the provider even exists
    if (provider == undefined)
    {
      return;
    }

    // hide the conenct wallet button if the user is already logged in
    if (provider.selectedAddress != null)
    {
        $('#connect-btn').hide();
    }

    // check if the user is conected (and connect if necessary)
    if (!provider.isConnected())
    {
      // prompt the user to change their chain if it is incorrect
      if (provider.chainId != CHAIN_STRING)
      {
        setChain();
      }
    }
}

// only set up the document if the window is ethereum
if (provider != undefined)
{
  /**********************************************************/
  /* Handle chain (network) and chainChanged (per EIP-1193) */
  /**********************************************************/
  provider.on('chainChanged', handleChainChanged);


  /***********************************************************/
  /* Handle user accounts and accountsChanged (per EIP-1193) */
  /***********************************************************/

  provider
    .request({ method: 'eth_accounts' })
    .then(handleAccountsChanged)
    .catch((err) => {
      // Some unexpected error.
      // For backwards compatibility reasons, if no accounts are available,
      // eth_accounts will return an empty array.
      console.error(err);
    });

  // Note that this event is emitted on page load.
  // If the array of accounts is non-empty, you're already
  // connected.
  provider.on('accountsChanged', handleAccountsChanged);

  // call the load document function
  loadDocument();
}


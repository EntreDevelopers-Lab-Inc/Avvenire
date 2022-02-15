// set the chain
async function setChain() {
    try {
      await ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: CHAIN_ID }],
      });

    } catch (switchError) {
      // This error code indicates that the chain has not been added to MetaMask.
      if (switchError.code === 4902) {
        try {
          await ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [
              {
                chainId: CHAIN_ID,
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

async function connect()
{
    ethereum.request({ method: 'eth_requestAccounts' });

    // reload the page
    window.location.reload();


    setChain();
}


// account change listener
ethereum.on('accountsChanged', function (accounts) {
    // set the correct chain
    setChain();
});

// make a document load function
function loadDocument() {
    // remove the conenct wallet button if the user is already logged in
    if (ethereum.selectedAddress != null)
    {
        $('#connect-btn').remove();
    }
}


// call the load document function
loadDocument();

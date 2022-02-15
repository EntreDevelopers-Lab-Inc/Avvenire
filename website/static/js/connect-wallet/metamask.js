let provider;
let accounts;

let accountAddress = "";
let signer;

async function connect()
{
    ethereum.request({ method: 'eth_requestAccounts' });

    try {
      await ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x1' }],
      });

    fetch('login', {
    method: 'post',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify([ethereum.selectedAddress])
  }).then((response) => {
    return response.json();
  })
  .then((data) => {
    // assign the cookie
    if (data['token'] != null)
    {
        document.cookie = 'token=' + data['token'];
        location.href = '/';
    }

  });

    } catch (switchError) {
      // This error code indicates that the chain has not been added to MetaMask.
      if (switchError.code === 4902) {
        try {
          await ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [
              {
                chainId: '0xf00',
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

/*
function login()
{

rightnow = (Date.now()/1000).toFixed(0)
sortanow = rightnow-(rightnow%600)

signer.signMessage("Signing in to Avvenire at "+sortanow, accountAddress, "")
            .then((signature) => {               handleAuth(accountAddress, signature)
            });
}

function handleAuth(accountAddress, signature)
{
  fetch('login', {
    method: 'post',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify([accountAddress,signature])
  }).then((response) => {
    return response.json();
  })
  .then((data) => {
    // assign the cookie
    document.cookie = 'token=' + data['token'];

    location.href = '/';
  });

}

async function connect() {
    ethereum.request({method: 'eth_requestAccounts'}).then(function () {

        provider = new ethers.providers.Web3Provider(web3.currentProvider);


        provider.getNetwork().then(function (result) {
            if (result['chainId'] != 1) {  // chain ID remains the same regardless of the network choices of users (1 is always mainnet)
                alert('Switch to Mainnet!');

            } else { // okay, confirmed we're on mainnet

                provider.listAccounts().then(function (result) {
                    // accountAddress = result[0]; // figure out the user's Eth address

                    // get a signer object so we can do things that need signing
                    signer = provider.getSigner();

                    // log the user in
                    login();

                    // redirect to home
                })
            }
        })
    })

}
*/
// connect by default (disabled)
// connect();

/*
web3.eth.getAccounts()
        .then((response) => {
            const publicAddressResponse = response[0];

            if (!(typeof publicAddressResponse === "undefined")) {
                setPublicAddress(publicAddressResponse);
                getNonce(publicAddressResponse);
            }
        })
        .catch((e) => {
            console.error(e);
        });
*/

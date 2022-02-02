let provider;
let accounts;

let accountAddress = "";
let signer;

function login()
{

  console.log('oh hey there');

 // signer.signMessage("hello");

rightnow = (Date.now()/1000).toFixed(0)
sortanow = rightnow-(rightnow%600)

signer.signMessage("Signing in to Avvenire at "+sortanow, accountAddress, "")
            .then((signature) => {               handleAuth(accountAddress, signature)
            });
}

function handleAuth(accountAddress, signature)
{
  console.log(accountAddress);
  console.log(signature);

  fetch('login', {
    method: 'post',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify([accountAddress,signature])
  }).then((response) => {
    return response.json();
  })
  .then((data) => {
    console.log(data);

    document.cookie = 'token=' + data['token'];

    location.href = '/';
  });

}

function connect() {
    console.log('connecting');
    ethereum.enable().then(function () {

        provider = new ethers.providers.Web3Provider(web3.currentProvider);


        provider.getNetwork().then(function (result) {
            if (result['chainId'] != 1) {
                alert('Switch to Mainnet!');

            } else { // okay, confirmed we're on mainnet

                provider.listAccounts().then(function (result) {
                    accountAddress = result[0]; // figure out the user's Eth address

                    provider.getBalance(String(result[0])).then(function (balance) {
                        var myBalance = (balance / ethers.constants.WeiPerEther).toFixed(4);
                    });

                    // get a signer object so we can do things that need signing
                    signer = provider.getSigner();

                    // log the user in
                    login();

                    // redirect to home
                    // location.href = '/'
                })
            }
        })
    })

}

// connect by default
connect();

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

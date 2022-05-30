import discord
from web3 import Web3

TOKEN = 'OTgwODYyOTc3NDY3MTA5Mzc2.GwGedS.RIBFqTu0uavUwasdius4OAlj3mFdyEW3wqy_E4'
INFURA_URL = 'https://mainnet.infura.io/v3/13ea03ccb69640b0933a55848596c54f'

client = discord.Client()
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# make a set of all the clients served
served = set()


@client.event
async def on_ready():
    print(f"{client.user} has connected to discord!")
    print(f"Guilds: {client.guilds}")
    print(f"Web3 Connected: {w3.isConnected()}")


# respond to messages
@client.event
async def on_message(message):
    # return if self
    if message.author == client.user:
        return

    # check if the message is a valid ethereum address
    if w3.isAddress(message.content):
        # print if so (going to be an API call later)
        print(message.content)

        # add the user to the served list if applicable
        if (message.author in served):
            resp = f"{message.author.mention}, you only get 2 free drinks!"
        else:
            served.add(message.author)
            resp = f"{message.author.mention} gets 2 free drinks (redeemable from {message.content})!"

        # send that the address was added
        await message.channel.send(resp)


# log errors in console
@client.event
async def on_error(event, *args, **kwargs):
    print(f"Error: {args[0]}")


if __name__ == "__main__":
    # run the bot
    client.run(TOKEN)

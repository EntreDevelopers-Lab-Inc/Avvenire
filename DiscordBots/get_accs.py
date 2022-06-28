import discord
import pandas as pd

TOKEN = 'OTgwODYyOTc3NDY3MTA5Mzc2.GwGedS.RIBFqTu0uavUwasdius4OAlj3mFdyEW3wqy_E4'
CHANNEL_ID = '989304902180302928'

client = discord.Client()

# make a set of all the addresses
addresses = set()


@client.event
async def on_ready():
    print(f"{client.user} has connected to discord!")
    print(f"Guilds: {client.guilds}")

    # get the channel
    for c in client.guilds[-1].channels:
        if c.name == 'wl-wallets':
            channel = c
            break

    # iterate over all the addresses in the chat
    print(channel)

    # export all the addresses to a dataframe
    messages = await channel.history(limit=10000).flatten()
    df = pd.DataFrame([{'author': message.author.name,
                        'address': message.content} for message in messages])
    df.to_csv('messages.csv', index=False)

    print('Exported messages')


# log errors in console
@client.event
async def on_error(event, *args, **kwargs):
    print(f"Error: {args[0]}")


if __name__ == "__main__":
    # run the bot
    client.run(TOKEN)

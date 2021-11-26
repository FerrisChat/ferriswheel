import ferris

client = ferris.Client()  # Create the FerrisWheel client


@client.listen()
async def on_message(message):
    if message.content == "ping":  # Message's content is ping
        await message.channel.send("pong")  # Send message "pong" to the channel


client.run(
    email="...", password="..."
)  # Run the client using email and password, which will connect to the FerrisChat server

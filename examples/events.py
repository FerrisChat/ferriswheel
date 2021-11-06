import ferris

client = ferris.Client() # Create the FerrisWheel client

@client.listen()
async def on_message(message):
    print("Received message:", message)

@client.listen()
async def on_message_edit(old, new):
    print("Message edited:", old, new)

@client.listen()
async def on_ready():
    g = await client.create_guild(name="Test Guild")
    c = await g.create_channel(name="Test Channel")
    m = await c.send_message("Hello world!") # Trigger on_message event
    await m.edit(content="Hello world!") # Trigger on_message_edit event

client.run(email="...", password="...") # Run the client using email and password, which will connect to the FerrisChat server
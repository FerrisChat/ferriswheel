import ferris

client = ferris.Client(
    max_messages_count=1000
)  # Create the FerrisWheel client, and store at most 1000 messages in cache, which is the default

client.run(
    email="...", password="..."
)  # Run the client using email and password, which will connect to the FerrisChat server

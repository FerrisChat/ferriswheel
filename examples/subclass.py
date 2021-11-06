import ferris

class Client(ferris.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.super_suspicious_var = "amogus"
    
    async def on_ready(self):
        print(self.super_suspicious_var)

client = Client() # Create an instance of the subclassed client

client.run(email="...", password="...") # Run the client using email and password, which will connect to the FerrisChat server
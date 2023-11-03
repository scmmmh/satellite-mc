"""Base server class for the API server."""
from microdot_asyncio import Microdot
from microdot_cors import CORS


server = Microdot()
cors = CORS(server, allowed_origins="*")

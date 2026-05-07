import asyncio
import uvicorn
import os
from dotenv import load_dotenv
from backend.opcua_server import PCBOPCUAServer
import backend.api as api

load_dotenv()

async def main():
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    
    # Configure and start FastAPI Server using Uvicorn
    print(f"Starting FastAPI Server on http://{api_host}:{api_port} ...")
    config = uvicorn.Config(app=api.app, host=api_host, port=api_port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run uvicorn server in the existing event loop
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servers stopped.")

import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Forçar UTF-8 para entrada/saída
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

async def main():
    print("Starting test...")
    server_path = os.path.abspath("server/app/main.py")
    
    print(f"Initializing with server at: {server_path}")
    if not os.path.exists(server_path):
        raise FileNotFoundError(f"Server file not found: {server_path}")
        
    # Usando o caminho completo do Python
    python_exe = sys.executable
    server_params = StdioServerParameters(
        command=python_exe,
        args=["-u", server_path],  # -u força saída sem buffer
    )
    
    print("Creating stdio client...")
    try:
        async with stdio_client(server_params) as (read, write):
            print("Client created, attempting to read initial server output...")
            
            # Tentar ler qualquer saída inicial do servidor
            try:
                initial_data = await asyncio.wait_for(read(), timeout=5.0)
                print(f"Initial server output: {initial_data}")
            except asyncio.TimeoutError:
                print("No initial server output received after 5 seconds")
            except Exception as e:
                print(f"Error reading initial output: {e}")
            
            print("Creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, attempting to initialize...")
                try:
                    await asyncio.wait_for(session.initialize(), timeout=10.0)
                    print("Session initialized successfully!")
                    
                    print("Listing tools...")
                    response = await session.list_tools()
                    print(f"Tools available: {response.tools}")
                except asyncio.TimeoutError:
                    print("Session initialization timed out after 10 seconds")
                except Exception as e:
                    print(f"Error during session initialization: {type(e).__name__}: {str(e)}")
                    raise
    except Exception as e:
        print(f"Error creating client: {type(e).__name__}: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

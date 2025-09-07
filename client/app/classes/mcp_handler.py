import asyncio
import os
import sys
from contextlib import asynccontextmanager, suppress
from classes.mcp_client import McpClient

class MCPHandler:
    def __init__(self):
        self.client = None
        self._lock = asyncio.Lock()
        if sys.platform == "win32":
            # Força o uso do ProactorEventLoop no Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    @asynccontextmanager
    async def get_client(self, tool_path):
        async with self._lock:  # Previne múltiplos acessos simultâneos
            try:
                print("\n=== Starting MCP Client Session ===")
                print(f"Tool path (original): {tool_path}")
                
                # Verifica se o caminho existe
                abs_tool_path = os.path.abspath(tool_path)
                print(f"Tool path (absolute): {abs_tool_path}")
                
                if not os.path.exists(abs_tool_path):
                    raise FileNotFoundError(f"Server file not found at: {abs_tool_path}")
                
                # Tenta reutilizar o cliente existente se estiver em bom estado
                if self.client and hasattr(self.client, 'session') and self.client.session:
                    try:
                        print("Testing existing client...")
                        # Adiciona timeout de 5 segundos para o teste
                        try:
                            await asyncio.wait_for(self.client.get_tools(), timeout=5.0)
                            print("Existing client is healthy, reusing it")
                            yield self.client
                            return
                        except asyncio.TimeoutError:
                            print("Health check timed out, creating new client")
                            await self.cleanup()
                        except Exception as e:
                            print(f"Client health check failed: {str(e)}")
                            await self.cleanup()
                    except Exception as e:
                        print(f"Error during client health check: {str(e)}")
                        await self.cleanup()
                
                # Cria e inicializa um novo cliente
                print("Creating new MCP client...")
                self.client = McpClient()
                
                if not tool_path:
                    raise ValueError("Tool path is empty")
                    
                print(f"Initializing MCP client with command: mcp run {abs_tool_path}")
                await self.client.initialize_with_stdio("mcp", ["run", abs_tool_path])
                print("MCP client initialization complete")
                
                # Verifica se o cliente está realmente inicializado
                if not self.client.session:
                    raise RuntimeError("Client session not initialized")
                
                print("MCP client session verified and ready")
                
                yield self.client
            except Exception as e:
                print(f"Error in MCP client session: {str(e)}")
                if self.client:
                    print("Cleaning up client due to error...")
                    await self.cleanup()
                raise
            finally:
                print("=== MCP Client Session Complete ===")
                # Mantemos o cliente vivo para reutilização
    
    async def cleanup(self):
        """Limpa o cliente MCP atual."""
        if self.client:
            try:
                print("Starting MCP client cleanup...")
                try:
                    await asyncio.wait_for(self.client.cleanup(), timeout=5.0)
                    print("MCP client cleanup successful")
                except asyncio.TimeoutError:
                    print("Cleanup timed out, forcing cleanup")
                    if hasattr(self.client, 'exit_stack'):
                        await self.client.exit_stack.aclose()
                except Exception as e:
                    print(f"Error during cleanup: {str(e)}")
                    if hasattr(self.client, 'exit_stack'):
                        await self.client.exit_stack.aclose()
            finally:
                self.client = None
                print("Client reference cleared")
    
    def __del__(self):
        # Garante que o cleanup seja chamado quando o objeto é destruído
        if self.client:
            try:
                # Cria um novo loop para o cleanup
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.cleanup())
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            except Exception:
                pass

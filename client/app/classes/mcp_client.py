import os
import asyncio
from mcp import ClientSession, Resource, StdioServerParameters, Tool
from mcp.types import Prompt, CallToolResult, ReadResourceResult, GetPromptResult
from mcp.client.stdio import stdio_client          
from mcp.client.sse import sse_client               
from contextlib import AsyncExitStack               

class McpClient:
    def __init__(self): 
        self.server_params: StdioServerParameters = None  
        self.session: ClientSession = None                
        self.exit_stack = AsyncExitStack()     
        self._debug = True          

    def _debug_log(self, msg: str):
        if self._debug:
            import sys
            with open("client.log", "a") as f:
                f.write(f"{msg}\n")
                f.flush()
            sys.stdout.flush()

    # async def initialize_with_stdio(self, command: str, args: list):
    #     try:
    #         self._debug_log("\n=== Starting MCP Client Initialization ===")
    #         self._debug_log(f"Command: {command}")
    #         self._debug_log(f"Args: {args}")
            
    #         # Valida o caminho do servidor
    #         server_path = args[1] if len(args) > 1 else None
    #         if server_path:
    #             self._debug_log(f"Checking server path: {server_path}")
    #             if not os.path.exists(server_path):
    #                 raise FileNotFoundError(f"Server file not found: {server_path}")
    #             self._debug_log("Server file exists")
            
    #         self.server_params = StdioServerParameters(
    #             command=command,
    #             args=args,
    #         )
    #         self._debug_log("Server parameters configured successfully")
            
    #         try:
    #             self.client = await asyncio.wait_for(
    #                 self.exit_stack.enter_async_context(stdio_client(self.server_params)),
    #                 timeout=10.0
    #             )
    #             self._debug_log("Stdio client created successfully")
    #             read, write = self.client
    #             self._debug_log("Read/write streams obtained successfully")
                
    #             self.session = await asyncio.wait_for(
    #                 self.exit_stack.enter_async_context(ClientSession(read, write)),
    #                 timeout=10.0
    #             )
    #             self._debug_log("Client session context entered")
                
    #             await asyncio.wait_for(self.session.initialize(), timeout=10.0)
    #             self._debug_log("Session initialized successfully")
                
    #             # Verifica se conseguimos listar as tools
    #             tools = await asyncio.wait_for(self.get_tools(), timeout=10.0)
    #             self._debug_log(f"Initial tools check: Found {len(tools)} tools")
                
    #         except asyncio.TimeoutError as te:
    #             self._debug_log("Operation timed out during initialization")
    #             raise RuntimeError("MCP client initialization timed out") from te
            
    #     except Exception as e:
    #         self._debug_log(f"Error in initialize_with_stdio: {str(e)}")
    #         raise e

    async def initialize_with_stdio(self, command: str, args: list):
        self.server_params = StdioServerParameters(
            command=command,
            args=args,
        )

        self.client = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
        read, write = self.client 

        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        await self.session.initialize()


    async def initialize_with_sse(self, host: str):
        self.client = await self.exit_stack.enter_async_context(sse_client(host))
        read, write = self.client

        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        await self.session.initialize()

    async def get_tools(self) -> list[Tool]:
        response = await self.session.list_tools()
        return response.tools

    async def get_resources(self) -> list[Resource]:
        response = await self.session.list_resources()
        return response.resources

    async def get_prompts(self) -> list[Prompt]:
        response = await self.session.list_prompts()
        return response.prompts

    async def call_tool(self, tool_name: str, args: dict[str, object]) -> CallToolResult:
        return await self.session.call_tool(tool_name, arguments=args)

    async def get_resource(self, uri: str) -> ReadResourceResult:
        return await self.session.read_resource(uri)

    async def invoke_prompt(self, prompt_name: str, args) -> GetPromptResult:
        return await self.session.get_prompt(prompt_name, arguments=args)

    def format_tools_llm(self, tools) -> list[object]:
        formatted_tools = []
        for tool in tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            })
        return formatted_tools

    async def cleanup(self) -> None:
        await self.exit_stack.aclose()

    # async def cleanup(self) -> None:
    #     """
    #     Limpa os recursos do cliente MCP.
    #     Tenta fazer um cleanup suave mantendo a conexão se possível.
    #     """
    #     try:
    #         self._debug_log("Starting cleanup...")
            
    #         if hasattr(self, 'session') and self.session:
    #             self._debug_log("Cleaning up session...")
    #             self.session = None
            
    #         if hasattr(self, 'client'):
    #             self._debug_log("Cleaning up client...")
    #             self.client = None
            
    #         if hasattr(self, 'server_params'):
    #             self._debug_log("Cleaning up server params...")
    #             self.server_params = None
            
    #         # Cria um novo exit_stack para futuras conexões
    #         self._debug_log("Resetting exit stack...")
    #         self.exit_stack = AsyncExitStack()
            
    #         self._debug_log("Cleanup completed successfully")
    #     except Exception as e:
    #         self._debug_log(f"Error during cleanup: {str(e)}")
    #         # Se houver erro, tenta um cleanup mais agressivo
    #         try:
    #             await self.exit_stack.aclose()
    #             self.exit_stack = AsyncExitStack()
    #         except Exception as e2:
    #             self._debug_log(f"Error during force cleanup: {str(e2)}")
    #         raise e
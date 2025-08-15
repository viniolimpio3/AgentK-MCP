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

    async def initialize_with_stdio(self, command: str, args: list):
        try:
            self._debug_log("\n=== Starting MCP Client Initialization ===")
            self._debug_log(f"Command: {command}")
            self._debug_log(f"Args: {args}")
            
            self.server_params = StdioServerParameters(
                command=command,
                args=args,
            )
            self._debug_log("Server parameters configured successfully")
            
            self.client = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
            self._debug_log("Stdio client created successfully")
            read, write = self.client
            self._debug_log("Read/write streams obtained successfully")
            
            self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            self._debug_log("Client session context entered")
            
            await self.session.initialize()
            self._debug_log("Session initialized successfully")
            
        except Exception as e:
            self._debug_log(f"Error in initialize_with_stdio: {str(e)}")
            raise e

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
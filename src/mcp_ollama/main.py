#!/usr/bin/env python3
"""Ollama MCP Server for AI-powered trading chatbot"""

import asyncio
import json
import logging
import aiohttp
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Ollama MCP Server",
    instructions="""
    This server integrates with Ollama to provide AI language model capabilities for trading chatbot.
    It supports chat completion, model management, and natural language processing for trading commands.
    """,
)


class ChatMessage(BaseModel):
    """Chat message structure"""

    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request"""

    model: str = Field(..., description="Model name to use")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    stream: bool = Field(default=False, description="Stream response")
    options: Dict[str, Any] = Field(default_factory=dict, description="Additional options")


class ModelInfo(BaseModel):
    """Ollama model information"""

    name: str
    size: int
    digest: str
    details: Dict[str, Any]
    modified_at: str


class OllamaClient:
    """Client for Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Ollama"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {e}")

    async def list_models(self) -> List[ModelInfo]:
        """List available models"""
        data = await self._request("GET", "/api/tags")
        models_data = data.get("models", [])
        return [ModelInfo(**model) for model in models_data]

    async def chat_completion(self, request: ChatRequest) -> Dict[str, Any]:
        """Generate chat completion"""
        request_data = request.model_dump()
        return await self._request("POST", "/api/chat", json=request_data)

    async def generate_completion(self, model: str, prompt: str, stream: bool = False) -> Dict[str, Any]:
        """Generate text completion"""
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        return await self._request("POST", "/api/generate", json=data)

    async def pull_model(self, model: str) -> Dict[str, Any]:
        """Pull/download a model"""
        data = {"name": model}
        return await self._request("POST", "/api/pull", json=data)

    async def delete_model(self, model: str) -> Dict[str, Any]:
        """Delete a model"""
        data = {"name": model}
        return await self._request("DELETE", "/api/delete", json=data)

    async def check_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            versions = await self._request("GET", "/api/version")
            return "version" in versions
        except Exception:
            return False


# Global Ollama client instance
ollama_client: Optional[OllamaClient] = None


async def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client"""
    global ollama_client
    if ollama_client is None:
        ollama_client = OllamaClient()
        await ollama_client.__aenter__()
    return ollama_client


@mcp.tool()
async def check_ollama_health() -> Dict[str, Any]:
    """
    Check if Ollama service is running and accessible.

    Returns:
        Dict[str, Any]: Health check result with status and available models
    """
    try:
        async with OllamaClient() as client:
            healthy = await client.check_health()
            if not healthy:
                return {"status": "unhealthy", "available_models": [], "error": "Ollama not responding"}

            models = await client.list_models()
            model_names = [model.name for model in models]

            return {
                "status": "healthy",
                "available_models": model_names,
                "model_count": len(model_names)
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def get_available_models() -> List[str]:
    """
    Get list of available Ollama models.

    Returns:
        List[str]: List of available model names
    """
    try:
        async with OllamaClient() as client:
            models = await client.list_models()
            return [model.name for model in models]
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise ValueError(f"Failed to get available models: {e}")


@mcp.tool()
async def chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> Dict[str, Any]:
    """
    Generate chat completion using Ollama models.

    Args:
        model: Model name to use (e.g., 'qwen2.5-coder', 'llama3.1')
        messages: List of messages in format [{"role": "user", "content": "Hello"}]
        stream: Whether to stream the response (not supported in MCP context)
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Dict[str, Any]: Chat completion response
    """
    try:
        # Convert messages to proper format
        chat_messages = [ChatMessage(**msg) for msg in messages]

        request = ChatRequest(
            model=model,
            messages=chat_messages,
            stream=stream,
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )

        async with OllamaClient() as client:
            response = await client.chat_completion(request)
            return response

    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise ValueError(f"Chat completion failed: {e}")


@mcp.tool()
async def generate_text(
    model: str,
    prompt: str,
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    """
    Generate text completion using Ollama models.

    Args:
        model: Model name to use
        prompt: Text prompt
        stream: Whether to stream the response
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        str: Generated text response
    """
    try:
        async with OllamaClient() as client:
            response = await client.generate_completion(model, prompt, stream)
            return response.get("response", "")
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise ValueError(f"Text generation failed: {e}")


@mcp.tool()
async def pull_model(model_name: str) -> Dict[str, Any]:
    """
    Pull/download a model from Ollama library.

    Args:
        model_name: Model name to pull (e.g., 'qwen2.5-coder', 'llama3.1:8b')

    Returns:
        Dict[str, Any]: Pull operation status
    """
    try:
        async with OllamaClient() as client:
            result = await client.pull_model(model_name)
            return {"status": "success", "model": model_name, "details": result}
    except Exception as e:
        logger.error(f"Failed to pull model {model_name}: {e}")
        return {"status": "error", "model": model_name, "error": str(e)}


@mcp.tool()
async def delete_model(model_name: str) -> Dict[str, Any]:
    """
    Delete a model from Ollama.

    Args:
        model_name: Model name to delete

    Returns:
        Dict[str, Any]: Delete operation status
    """
    try:
        async with OllamaClient() as client:
            result = await client.delete_model(model_name)
            return {"status": "success", "model": model_name}
    except Exception as e:
        logger.error(f"Failed to delete model {model_name}: {e}")
        return {"status": "error", "model": model_name, "error": str(e)}


@mcp.tool()
async def analyze_trading_intent(message: str) -> Dict[str, Any]:
    """
    Analyze user message to determine trading intent and extract parameters.

    Args:
        message: User message to analyze

    Returns:
        Dict[str, Any]: Analysis result with intent, parameters, and confidence
    """
    prompt = f"""
    Analyze the following user message for trading intent. Determine if they want to:
    - Buy or sell assets
    - Check account status
    - Get market data
    - Place/modify/cancel orders
    - Get analysis or predictions

    If it's a trading command, extract:
    - Action (buy, sell, check, etc.)
    - Symbol (currency pair, stock, etc.)
    - Volume/amount
    - Price levels (entry, stop loss, take profit)
    - Timeframe

    Message: "{message}"

    Respond in JSON format:
    {{
        "intent": "trade|info|analysis|other",
        "action": "buy|sell|check|cancel|modify|null",
        "symbol": "extracted symbol or null",
        "volume": "extracted volume or null",
        "price": "entry price or null",
        "stop_loss": "SL price or null",
        "take_profit": "TP price or null",
        "timeframe": "M1|H1|D1 etc or null",
        "confidence": 0.0-1.0,
        "parsed_command": "human readable summary of intent"
    }}
    """

    try:
        async with OllamaClient() as client:
            response = await client.generate_completion(
                model="qwen2.5-coder",
                prompt=prompt,
                stream=False,
                temperature=0.1  # Low temperature for consistent analysis
            )

        response_text = response.get("response", "{}").strip()

        # Extract JSON from response
        try:
            # Try to parse as JSON directly
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from text response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    "intent": "other",
                    "confidence": 0.0,
                    "parsed_command": f"Could not parse: {response_text[:100]}"
                }

        return result

    except Exception as e:
        logger.error(f"Trading intent analysis failed: {e}")
        return {
            "intent": "error",
            "confidence": 0.0,
            "error": str(e),
            "parsed_command": "Analysis failed"
        }


@mcp.resource("ollama://models")
def get_models_resource() -> str:
    """
    Get information about available Ollama models.

    Returns:
        str: Formatted model information
    """
    # This is a synchronous resource, we can't make async calls here
    # Return placeholder that will be used by tools
    return "Use list_models tool to get current model information"


@mcp.resource("ollama://health")
def get_health_resource() -> str:
    """
    Get Ollama service health information.

    Returns:
        str: Health status
    """
    return "Use check_health tool to get current health status"


@mcp.resource("ollama://trading-models")
def get_trading_models_resource() -> str:
    """
    Get recommended models for trading analysis.

    Returns:
        str: Recommended trading models
    """
    models = """
    Recommended Ollama models for trading chatbot:

    1. qwen2.5-coder - Good for trading command parsing and code generation
    2. llama3.1 - Good for natural language understanding and analysis
    3. deepseek-r1 - Excellent for financial reasoning and predictions
    4. codellama - Good for technical analysis and indicator calculations

    Pull models using: ollama pull <model-name>
    """
    return models


@mcp.tool()
def health() -> dict[str, Any]:
    """Health check for Ollama MCP server"""
    try:
        # Check if Ollama service is running
        ollama_health = check_ollama_health()
        return {
            "status": "available" if ollama_health else "unavailable",
            "service": "Ollama MCP Server",
            "ollama_connected": ollama_health,
            "models_available": get_available_models() if ollama_health else [],
            "port": 8001
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "Ollama MCP Server",
            "error": str(e),
            "port": 8001
        }


if __name__ == "__main__":
    import os
    import argparse

    # Check if running in MCP mode or HTTP server mode
    if os.getenv("OLLAMA_MCP_TRANSPORT") == "stdio":
        # Running as MCP server via stdio
        mcp.run()
    elif os.getenv("OLLAMA_MCP_MODE") == "http":
        # Running as simple HTTP server for demo
        print("Starting Ollama MCP HTTP Server on port 8001...")

        # Simple HTTP server using built-in
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        from urllib.parse import urlparse, parse_qs

        class OllamaMockHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"status": "available", "service": "Ollama MCP Server", "port": 8001}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == '/chat':
                    try:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()

                        # Mock Ollama response for demo
                        response = {
                            "id": str(uuid.uuid4()),
                            "result": {
                                "message": {
                                    "content": "Olá! Sou seu assistente de trading inteligente. Sua mensagem foi processada com sucesso!"
                                }
                            }
                        }
                        self.wfile.write(json.dumps(response).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        error_response = {"error": str(e)}
                        self.wfile.write(json.dumps(error_response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

        try:
            server = HTTPServer(('127.0.0.1', 8001), OllamaMockHandler)
            print("Ollama Mock HTTP Server running on port 8001")
            server.serve_forever()
        except Exception as e:
            print(f"Server error: {e}")
    else:
        # Running standalone - print info
        print("Ollama MCP Server")
        print("Set OLLAMA_MCP_TRANSPORT=stdio for MCP mode")
        print("Set OLLAMA_MCP_MODE=http for HTTP server mode")

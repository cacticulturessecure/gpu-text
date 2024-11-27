import httpx
import json
import asyncio
import logging
from typing import AsyncGenerator, List
from datetime import datetime
import uuid

from app.models.chat import ChatMessage, ChatCompletionResponse, ChatCompletionStreamResponse
from app.core.config import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.timeout = 300.0
        logger.debug(f"Initialized OllamaService with URL: {self.base_url}, model: {self.model}, timeout: {self.timeout}s")
        
    async def _make_request(self, endpoint: str, data: dict) -> dict:
        """Make a request to Ollama API and accumulate streaming response."""
        url = f"{self.base_url}/api/{endpoint}"
        logger.debug(f"Making request to {url} with data: {data}")
        try:
            accumulated_response = ""
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=data) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if chunk.get("message", {}).get("content"):
                                    accumulated_response += chunk["message"]["content"]
                                if chunk.get("done", False):
                                    return {
                                        "message": {
                                            "role": "assistant",
                                            "content": accumulated_response
                                        },
                                        "usage": chunk.get("usage", {})
                                    }
                            except json.JSONDecodeError:
                                continue
            return {
                "message": {
                    "role": "assistant",
                    "content": accumulated_response
                },
                "usage": {}
            }
        except Exception as e:
            logger.error(f"Error making request: {str(e)}", exc_info=True)
            raise

    def _format_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Format messages for Ollama API."""
        formatted = [{"role": msg.role, "content": msg.content} for msg in messages]
        logger.debug(f"Formatted messages: {formatted}")
        return formatted

    def _create_response(self, ollama_response: dict, messages: List[ChatMessage]) -> ChatCompletionResponse:
        """Create a standardized response from Ollama output."""
        logger.debug(f"Creating response from Ollama response: {ollama_response}")
        return ChatCompletionResponse(
            id=str(uuid.uuid4()),
            model=self.model,
            created=int(datetime.now().timestamp()),
            message=ChatMessage(
                role="assistant",
                content=ollama_response["message"]["content"]
            ),
            usage=ollama_response.get("usage", {})
        )

    async def generate_chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: float = None,
        max_tokens: int = None
    ) -> ChatCompletionResponse:
        """Generate a chat completion."""
        logger.debug(f"Generating chat completion with messages: {messages}")
        data = {
            "model": self.model,
            "messages": self._format_messages(messages)
        }

        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens

        response = await self._make_request("chat", data)
        return self._create_response(response, messages)

    async def generate_chat_completion_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = None,
        max_tokens: int = None
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        """Generate a streaming chat completion."""
        data = {
            "model": self.model,
            "messages": self._format_messages(messages)
        }

        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens

        completion_id = str(uuid.uuid4())
        created = int(datetime.now().timestamp())

        try:
            url = f"{self.base_url}/api/chat"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=data) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if chunk.get("message", {}).get("content"):
                                    yield ChatCompletionStreamResponse(
                                        id=completion_id,
                                        model=self.model,
                                        created=created,
                                        delta=ChatMessage(
                                            role="assistant",
                                            content=chunk["message"]["content"]
                                        ),
                                        usage=chunk.get("usage") if chunk.get("done", False) else None
                                    )
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error in stream generation: {str(e)}")
            raise

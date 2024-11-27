import httpx
import json
import asyncio
from typing import AsyncGenerator, List
from datetime import datetime
import uuid

from app.models.chat import ChatMessage, ChatCompletionResponse, ChatCompletionStreamResponse
from app.core.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        
    async def _make_request(self, endpoint: str, data: dict) -> httpx.Response:
        """Make a request to Ollama API."""
        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response

    def _format_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Format messages for Ollama API."""
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def _create_response(self, ollama_response: dict, messages: List[ChatMessage]) -> ChatCompletionResponse:
        """Create a standardized response from Ollama output."""
        return ChatCompletionResponse(
            id=str(uuid.uuid4()),
            model=self.model,
            created=int(datetime.now().timestamp()),
            message=ChatMessage(
                role="assistant",
                content=ollama_response.get("message", {}).get("content", "")
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
        data = {
            "model": self.model,
            "messages": self._format_messages(messages),
            "stream": False
        }

        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens

        response = await self._make_request("chat", data)
        return self._create_response(response.json(), messages)

    async def generate_chat_completion_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = None,
        max_tokens: int = None
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        """Generate a streaming chat completion."""
        data = {
            "model": self.model,
            "messages": self._format_messages(messages),
            "stream": True
        }

        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens

        completion_id = str(uuid.uuid4())
        created = int(datetime.now().timestamp())

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", f"{self.base_url}/chat", json=data) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            yield ChatCompletionStreamResponse(
                                id=completion_id,
                                model=self.model,
                                created=created,
                                delta=ChatMessage(
                                    role="assistant",
                                    content=chunk.get("message", {}).get("content", "")
                                ),
                                usage=chunk.get("usage") if "done" in chunk else None
                            )
                        except json.JSONDecodeError:
                            continue

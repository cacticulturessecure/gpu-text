import httpx
import json
import asyncio
from typing import AsyncGenerator, List
from datetime import datetime
import uuid
import logging
from fastapi import HTTPException

from app.models.chat import ChatMessage, ChatCompletionResponse, ChatCompletionStreamResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.timeout = 300.0
        self.max_context_length = settings.MAX_CONTEXT_LENGTH
        
    async def _validate_token_count(self, messages: List[ChatMessage], max_tokens: int):
        # Estimate token count (rough estimation)
        estimated_tokens = sum(len(msg.content.split()) * 1.3 for msg in messages)
        if estimated_tokens + max_tokens > self.max_context_length:
            raise HTTPException(
                status_code=400,
                detail=f"Combined input and output tokens exceed model's context length of {self.max_context_length}"
            )

    async def generate_chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: float = None,
        max_tokens: int = None
    ) -> ChatCompletionResponse:
        # Validate token counts
        if max_tokens:
            await self._validate_token_count(messages, max_tokens)
            
        url = f"{self.base_url}/api/chat"
        data = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "stream": False
        }
        
        if temperature is not None:
            if not 0 <= temperature <= 2:
                raise HTTPException(status_code=400, detail="Temperature must be between 0 and 2")
            data["temperature"] = temperature
            
        if max_tokens is not None:
            if max_tokens > settings.MAX_CONTEXT_LENGTH:
                raise HTTPException(
                    status_code=400,
                    detail=f"max_tokens exceeds model's maximum context length of {settings.MAX_CONTEXT_LENGTH}"
                )
            data["max_tokens"] = max_tokens
            
        try:
            logger.info(
                f"Request stats: model={self.model}, "
                f"temperature={temperature}, "
                f"max_tokens={max_tokens}, "
                f"message_count={len(messages)}"
            )
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                
            return ChatCompletionResponse(
                id=str(uuid.uuid4()),
                model=self.model,
                created=int(datetime.now().timestamp()),
                message=ChatMessage(
                    role="assistant",
                    content=result["message"]["content"]
                ),
                usage=result.get("usage", {})
            )
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

    async def generate_chat_completion_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = None,
        max_tokens: int = None
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        if max_tokens:
            await self._validate_token_count(messages, max_tokens)
            
        url = f"{self.base_url}/api/chat"
        data = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "stream": True
        }
        
        if temperature is not None:
            if not 0 <= temperature <= 2:
                raise HTTPException(status_code=400, detail="Temperature must be between 0 and 2")
            data["temperature"] = temperature
            
        if max_tokens is not None:
            if max_tokens > settings.MAX_CONTEXT_LENGTH:
                raise HTTPException(
                    status_code=400,
                    detail=f"max_tokens exceeds model's maximum context length of {settings.MAX_CONTEXT_LENGTH}"
                )
            data["max_tokens"] = max_tokens

        completion_id = str(uuid.uuid4())
        created = int(datetime.now().timestamp())
        
        try:
            logger.info(
                f"Stream request stats: model={self.model}, "
                f"temperature={temperature}, "
                f"max_tokens={max_tokens}, "
                f"message_count={len(messages)}"
            )
            
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

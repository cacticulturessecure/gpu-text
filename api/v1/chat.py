from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from app.models.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse
)
from app.services.ollama import OllamaService

router = APIRouter(prefix="/api/v1")

async def get_ollama_service() -> OllamaService:
    return OllamaService()

@router.post("/chat", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    ollama_service: OllamaService = Depends(get_ollama_service)
) -> ChatCompletionResponse:
    return await ollama_service.generate_chat_completion(
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )

@router.post("/chat/stream")
async def create_chat_completion_stream(
    request: ChatCompletionRequest,
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    stream = ollama_service.generate_chat_completion_stream(
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    return StreamingResponse(
        stream_response(stream),
        media_type="text/event-stream"
    )

async def stream_response(stream):
    try:
        async for chunk in stream:
            yield f"data: {chunk.json()}\n\n"
    except Exception as e:
        yield f"data: [ERROR] {str(e)}\n\n"
    finally:
        yield "data: [DONE]\n\n"

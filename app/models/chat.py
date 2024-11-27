from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Individual chat message with role and content."""
    role: Literal["system", "user", "assistant"] = Field(
        description="The role of the message sender"
    )
    content: str = Field(
        description="The content of the message"
    )

class ChatCompletionRequest(BaseModel):
    """Request body for chat completion endpoint."""
    messages: List[ChatMessage] = Field(
        description="The messages to generate a response for",
        min_items=1
    )
    model: str = Field(
        default="llama2",
        description="The model to use for completion"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature between 0 and 2"
    )
    max_tokens: Optional[int] = Field(
        default=2000,
        gt=0,
        description="Maximum number of tokens to generate"
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response"
    )

class ChatCompletionResponse(BaseModel):
    """Response for chat completion endpoint."""
    id: str = Field(
        description="Unique identifier for the completion"
    )
    model: str = Field(
        description="The model used for completion"
    )
    created: int = Field(
        description="Unix timestamp of when the completion was created"
    )
    message: ChatMessage = Field(
        description="The generated response message"
    )
    usage: dict = Field(
        description="Token usage statistics for the completion"
    )

class ChatCompletionStreamResponse(BaseModel):
    """Response chunk for streaming chat completion."""
    id: str = Field(
        description="Unique identifier for the completion"
    )
    model: str = Field(
        description="The model used for completion"
    )
    created: int = Field(
        description="Unix timestamp of when the chunk was created"
    )
    delta: ChatMessage = Field(
        description="The partial message content for this chunk"
    )
    usage: Optional[dict] = Field(
        default=None,
        description="Token usage statistics (only included in final chunk)"
    )

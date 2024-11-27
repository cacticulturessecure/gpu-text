from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2000, gt=0, le=131072)
    stream: Optional[bool] = False
    context_length: Optional[int] = Field(default=131072, le=131072)

class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    created: int
    message: ChatMessage
    usage: dict

class ChatCompletionStreamResponse(BaseModel):
    id: str
    model: str
    created: int
    delta: ChatMessage
    usage: Optional[dict] = None

from datetime import datetime
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field

# --- Record ---
class RecordRequest(BaseModel):
    type: Literal["text", "image"]
    content: str = Field(..., min_length=1)
    mime_type: Optional[str] = None

class StagingItem(BaseModel):
    temp_id: int
    date: str
    amount: float
    main_category: str
    sub_category: Optional[str] = None
    payee: Optional[str] = None
    remark: Optional[str] = None
    consumer: Optional[str] = None
    is_essential: int = 0
    linked_asset: Optional[str] = None
    is_duplicate: bool = False
    confidence: float = 1.0

class RecordResponse(BaseModel):
    batch_id: str
    items: List[StagingItem]
    summary: str

class ConfirmRequest(BaseModel):
    batch_id: str
    action: Literal["confirm_all", "confirm", "modify", "reject_all"]
    temp_ids: Optional[List[int]] = None
    temp_id: Optional[int] = None
    modifications: Optional[dict] = None

class InteractionRequest(BaseModel):
    batch_id: str
    instruction: str

# --- Auth ---
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class APIKeyResponse(BaseModel):
    api_key: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    api_key: str

# --- Generic Response ---
class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str = "操作成功"

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class ConfigItem(BaseModel):
    name: str = Field(..., min_length=1)

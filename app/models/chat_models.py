from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    type: str = "user"  # "user" or "assistant"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ChatResponse(BaseModel):
    message: str
    type: str = "assistant"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    requires_confirmation: bool = False
    suggested_action: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ProjectStructure(BaseModel):
    project_name: str
    project_type: str = "web"
    include_keywords: bool = True
    include_variables: bool = True
    test_suites: list = []

class TestCase(BaseModel):
    name: str
    description: str
    keywords: list = []
    variables: Dict[str, str] = {}
    test_suite: str = "default" 
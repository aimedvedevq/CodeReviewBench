from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ModelType(Enum):
    VLLM = "vllm"
    OPENAI = "openai"

class ModelConfig(BaseModel):    
    model_type: ModelType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    gpu_memory_utilization: Optional[float] = 0.95
    model_path: str
    
    

from abc import ABC, abstractmethod
from transformers import AutoTokenizer
from configs.generation_config import GenerationConfig
from typing import Optional

class BaseLLM(ABC):
    @abstractmethod
    def __init__(self, model_path: str):
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def batch_generate(self, prompts: list[str], generation_config: GenerationConfig, system_prompt: Optional[str] = None) -> list[str]:
        pass
    
    @property
    @abstractmethod
    def type(self) -> str:
        pass
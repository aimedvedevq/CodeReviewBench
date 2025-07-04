from dataclasses import dataclass

@dataclass
class GenerationConfig:
    max_new_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.95

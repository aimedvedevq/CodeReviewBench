from vllm import LLM, SamplingParams
from typing import List, Optional, Dict, Any
from transformers import AutoTokenizer
from .base_model import BaseLLM
from vllm.sampling_params import GuidedDecodingParams
from pydantic import BaseModel
from configs.generation_config import GenerationConfig
from configs.model_config import ModelConfig

class VLLMLLM(BaseLLM):
    def __init__(self, model_config: ModelConfig):
        
        self.model_path = model_config.model_path
        self.llm = LLM(model=self.model_path, tensor_parallel_size=1, gpu_memory_utilization=model_config.gpu_memory_utilization)
        self._tokenizer = None
        
    def get_tokenizer(self) -> AutoTokenizer:

        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        return self._tokenizer

    def generate(self, prompt: str, system_prompt: Optional[str], generation_config: GenerationConfig, response_format: Optional[BaseModel] = None) -> str:

        if response_format:
            guided_decoding_params = GuidedDecodingParams(
                json=response_format.model_json_schema()
            )
        else:
            guided_decoding_params = None
            
        sampling_params = SamplingParams(
            temperature=generation_config.temperature,
            max_tokens=generation_config.max_new_tokens,
            guided_decoding=guided_decoding_params
        )
        
        messages = [] 
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        messages = [self._tokenizer.apply_chat_template(message, tokenize=False) for message in messages]
        
        outputs = self.llm.generate(messages, sampling_params)
        if response_format:
            return response_format.model_validate_json(outputs[0].outputs[0].text)
        else:
            return outputs[0].outputs[0].text

    def batch_generate(self, prompts: List[str],
                    generation_config: GenerationConfig,
                    system_prompt: Optional[str], 
                    response_format: Optional[str] = None
                    ) -> List[str]:

        if response_format:
            guided_decoding_params = GuidedDecodingParams(
                json=response_format.model_json_schema()
            )
        else:
            guided_decoding_params = None
            
        sampling_params = SamplingParams(
            temperature=generation_config.temperature,
            max_tokens=generation_config.max_new_tokens,
            guided_decoding=guided_decoding_params,
        )
        
        if system_prompt:
            messages = [
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
                for prompt in prompts
            ]
        else:
            messages = [
                [{"role": "user", "content": prompt}]
                for prompt in prompts
            ]
        
        messages = [self._tokenizer.apply_chat_template(message, tokenize=False) for message in messages]
        outputs = self.llm.generate(messages, sampling_params)
        if response_format:
            return [response_format.model_validate_json(output.outputs[0].text) for output in outputs]
        else:
            return [output.outputs[0].text for output in outputs]
    
    @property
    def type(self) -> str:
        return "vllm"
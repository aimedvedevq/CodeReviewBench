from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

class BaseMetric(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def calculate(self, references: List[str], hypothesis: List[List[str]], passes: List[int]) -> Tuple[pd.DataFrame, pd.Series]:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    def standard_error(self, df: pd.DataFrame) -> pd.Series:
        return df.std(axis=0) / (len(df) ** 0.5)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from src.models import ModelFactory
from src.strategies import StrategyFactory
from pydantic import BaseModel, Field, ConfigDict
from configs.model_config import ModelConfig
from configs.generation_config import GenerationConfig
from typing import List, Optional, Dict, Any
import uvicorn

app = FastAPI()

# In-memory store for strategies, keyed by a session or benchmark id
strategies_store: Dict[str, Any] = {}
model_factory = ModelFactory()
strategy_factory = StrategyFactory()

class BenchmarkConfig(BaseModel):
    model: ModelConfig = Field(..., alias="model_config")
    judge_model: ModelConfig = Field(..., alias="judge_model_config")
    metrics_to_compute: List[str]
    strategy_name: str

    # Enable population from field aliases (so clients can still send
    # "model_config" and "judge_model_config" in JSON payloads).
    model_config = ConfigDict(populate_by_name=True)

class EvaluationConfig(BaseModel):
    benchmark_id: str
    generation_config: GenerationConfig
    passes: List[int] = [1, 5, 10]

@app.post("/init_benchmark")
def init_benchmark(benchmark_config: BenchmarkConfig):
    model = model_factory.get_model(benchmark_config.model)
    judge_model = model_factory.get_model(benchmark_config.judge_model)
    metrics_to_compute = benchmark_config.metrics_to_compute
    strategy = strategy_factory.get_strategy(
        benchmark_config.strategy_name, model, judge_model, metrics_to_compute
    )
    # Generate a unique benchmark_id (could use uuid in production)
    benchmark_id = f"{benchmark_config.strategy_name}_{id(strategy)}"
    strategies_store[benchmark_id] = strategy
    return {"benchmark_id": benchmark_id}

@app.post("/run_benchmark")
def run_benchmark(evaluation_config: EvaluationConfig):
    """
    Runs the evaluation for a given benchmark_id and evaluation config.
    """
    benchmark_id = evaluation_config.benchmark_id
    strategy = strategies_store.get(benchmark_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Benchmark not found. Please initialize first.")
    results = strategy.evaluate(
        evaluation_config.generation_config, evaluation_config.passes
    )

    # Convert pandas objects to JSON-serialisable structures
    serialised_results: Dict[str, Any] = {}
    for metric_name, value in results.items():
        if value is None:
            serialised_results[metric_name] = None
            continue

        try:
            import pandas as pd
            if isinstance(value, tuple) and len(value) == 3:
                df, mean_series, std_series = value  # type: ignore

                if isinstance(df, pd.DataFrame):
                    df_json = df.to_dict(orient="records")
                else:
                    df_json = df  # fallback

                if isinstance(mean_series, pd.Series):
                    mean_json = mean_series.to_dict()
                else:
                    mean_json = mean_series

                if isinstance(std_series, pd.Series):
                    std_json = std_series.to_dict()
                else:
                    std_json = std_series

                serialised_results[metric_name] = {
                    "samples": df_json,
                    "mean": mean_json,
                    "std": std_json,
                }
            else:
                # Unknown structure, try jsonable_encoder directly
                serialised_results[metric_name] = jsonable_encoder(value)
        except Exception as e:
            # Fallback to string representation in case of failure
            serialised_results[metric_name] = str(value)

    return jsonable_encoder(serialised_results)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
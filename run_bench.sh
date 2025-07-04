#!/usr/bin/env bash
python benchmark_cli.py \
  --model-type openai \
  --model-path anthropic/claude-3.7-sonnet \
  --base-url https://openrouter.ai/api/v1 \
  --api-key $OPENROUTER_API_KEY \
  --judge-model-type openai \
  --judge-model-path qwen/qwen-2.5-coder-32b-instruct \
  --judge-base-url https://openrouter.ai/api/v1 \
  --judge-api-key $OPENROUTER_API_KEY \
  --metrics "llm_exact_match,bleu,multi_metric,chrf" \
  --passes "1,5,10" \
  --out-json agg.json \
  --out-jsonl samples.jsonl

  
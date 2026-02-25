#!/bin/bash
set -e

exec uvicorn src.ollama_deproxy.main:app \
  --host 0.0.0.0 \
  --port "${LOCAL_PORT:-11434}"
#!/bin/bash
ollama serve &

# Wait until Ollama is ready
until curl -s http://localhost:11434/api/tags >/dev/null; do
  echo "Waiting for Ollama..."
  sleep 2
done

# Pull model
ollama pull mistral

# Start FastAPI app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
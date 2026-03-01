def run():
    """Run the Ollama DeProxy application."""
    import os
    from pathlib import Path

    import uvicorn
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent.parent / ".env")

    port = os.getenv("local_port") or 11434
    uvicorn.run("ollama_deproxy.main:app", host="0.0.0.0", port=port, reload=False)

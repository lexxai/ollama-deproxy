def run():
    """Run the Ollama DeProxy application."""
    import uvicorn
    from ollama_deproxy.config import settings

    port = settings.local_port or 11434
    uvicorn.run("ollama_deproxy.main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    run()

__all__ = ["run"]

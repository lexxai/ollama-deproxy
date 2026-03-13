from time import sleep


def run():
    """Run the Ollama DeProxy application."""
    import os
    from pathlib import Path

    import uvicorn
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent.parent / ".env")

    port = int(os.getenv("local_port") or 11434)
    while True:
        uvicorn.run("ollama_deproxy.main:app", host="0.0.0.0", port=port, reload=False, log_config=None)
        try:
            print("\n\nSleeping for 10 sec before restarting server. Press Ctrl+C to exit.")
            sleep(10)
            print("Restarting server...")
        except KeyboardInterrupt:
            break
    print("Exiting...")

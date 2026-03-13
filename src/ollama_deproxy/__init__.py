import importlib.metadata

try:
    __version__ = importlib.metadata.version("ollama-deproxy")
except importlib.metadata.PackageNotFoundError:
    # Fallback for when the package is not "installed" (e.g., during local dev)
    def __getattr__(name):
        if name == "__version__":
            from .config import settings

            print(f"Using version from settings")
            return settings.app_version
        raise AttributeError(f"module {__name__} has no attribute {name}")


def run():
    """Run the Ollama DeProxy application."""
    import argparse
    from time import sleep
    import os
    import sys
    from pathlib import Path

    import uvicorn
    from dotenv import load_dotenv

    def print_header():
        from .get_version import app_version

        """Print decorative header with icons to console."""
        print("\n" + "=" * 60)
        print(f"🚀 Ollama DeProxy Server v{app_version()}")
        print("=" * 60)
        if sys.platform == "win32":
            os.system(f"title Ollama DeProxy Server 🚀 [{__version__}]")
        print()

    parser = argparse.ArgumentParser(description="Run the Ollama DeProxy application.")
    parser.add_argument("--remote-url", type=str, help="Override REMOTE_URL environment variable")
    parser.add_argument("--remote-auth-token", type=str, help="Override REMOTE_AUTH_TOKEN environment variable")
    parser.add_argument("--local-port", type=int, help="Override local_port environment variable")
    parser.add_argument("--log-level", type=str, help="Override log level environment variable")
    parser.add_argument("--env_path", type=str, help="Override path to .env file")
    parser.add_argument("--version", "-v", action="store_true", help="Version of the application")

    args = parser.parse_args()

    if args.version:
        print(f"Ollama DeProxy version: {__version__}")
        return

    env_path = Path(__file__).parent.parent.parent / ".env"

    if args.env_path:
        _env_path = Path(args.env_path)
        if _env_path.exists():
            env_path = _env_path
        else:
            print(f"Error: your .env file not found at {_env_path}. Used default .env file: {env_path}.")

    load_dotenv(env_path)

    if args.remote_url:
        os.environ["REMOTE_URL"] = args.remote_url

    if args.remote_auth_token:
        os.environ["REMOTE_AUTH_TOKEN"] = args.remote_auth_token

    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level

    if args.local_port:
        os.environ["LOCAL_PORT"] = str(args.local_port)

    port = int(os.getenv("local_port") or 11434)

    print_header()

    while True:
        uvicorn.run("ollama_deproxy.main:app", host="0.0.0.0", port=port, reload=False, log_config=None)
        try:
            print("\n\nSleeping for 10 sec before restarting server. Press Ctrl+C to exit.")
            sleep(10)
            print("Restarting server...")
        except KeyboardInterrupt:
            break
    print("Exiting...")

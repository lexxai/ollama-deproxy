import importlib.metadata

try:
    __version__ = importlib.metadata.version("ollama-deproxy")
except importlib.metadata.PackageNotFoundError:
    # Fallback for when the package is not "installed" (e.g., during local dev)
    from ollama_deproxy.utils.common import app_version

    __version__ = app_version()

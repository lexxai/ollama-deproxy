import importlib.metadata

try:
    __version__ = importlib.metadata.version("ollama-deproxy")
except importlib.metadata.PackageNotFoundError:
    # Fallback for when the package is not "installed" (e.g., during local dev)
    def __getattr__(name):
        if name == "__version__":
            from .get_version import app_version

            print("Using version from settings")
            return app_version()
        raise AttributeError(f"module {__name__} has no attribute {name}")

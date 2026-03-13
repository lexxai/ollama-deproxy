def app_version():
    from pathlib import Path

    BASE_PATH = Path(__file__).parent.parent

    v = "0.0.1"
    try:
        pyproject_file = BASE_PATH.parent / "pyproject.toml"
        if pyproject_file.exists():
            import tomllib

            with pyproject_file.open("rb") as f:
                v = tomllib.load(f)["project"]["version"]
    except Exception as e:
        print(f"Error app_version: {e}")
    return v

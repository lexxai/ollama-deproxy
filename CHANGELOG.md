Changelog
=====================

## [0.3.0] - 2026-02-28
### Added
* Caching of model names and their corresponding Ollama API endpoints
* Autodetection is the best hash algorithm for this platform
* Environment variables `CACHE_ENABLED`, `CACHE_MAXSIZE`, `CACHE_TTL`, `HASH_ALGORITHM`

### Changed
* Bumped a version to `0.3.0`
* Updated `ENVIRONMENT.md` to document new environment variables and usage details

## [0.2.0] - 2026-02-27

### Added
* Compatibility with standard OpenAI request format (for proxying and integration layers)
* Graceful handling of empty Ollama requests (e.g., sent by PyCharm AI Assistant)
* `OllamaHelper` class to encapsulate model name correction and request utilities
* Support for automatic correction of numbered model names (e.g., `4` → `qwen3-coder-next:latest`) when used with the GitHub Copilot plugin
  * Controlled via `CORRECT_NUMBERED_MODEL_NAMES` in `.env` (default: `false`)
* Optional request logging for debugging
  * Controlled via `DEBUG_REQUEST` in `.env` (default: `false`)

### Changed
* Bumped version to `0.2.0`
* Updated `ENVIRONMENT.md` to document new environment variables and usage details



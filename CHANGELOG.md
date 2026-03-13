Changelog
=====================

## [0.4.0] - 2026-03-12

### Added

* Environment variables `PATH_PROXY_OLLAMA` (default: `ollama/`) and `PATH_API` (default: `api/`) for configurable API path
  prefixes
* Dynamic path generation with `gen_path()` function supporting automatic prefix detection and correction
* Anthropic API compatibility layer with automatic path correction for endpoints like `v1/messages`
* OpenAI API compatibility with automatic path normalization for standard endpoints
* CLI argument support for overriding environment variables (use `--help` to view available options)

## [0.3.1] - 2026-03-05
### Added 
* if error for max_connections exceeded: `http_connection.re_connect()` 
* `get_duration_str` for logging duration of requests
* introduce `http_connection` and `semaphore`
* now Datetime in each logger message
* Bumped a version to `0.3.1`


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
0  * Controlled via `CORRECT_NUMBERED_MODEL_NAMES` in `.env` (default: `false`)
* Optional request logging for debugging
  * Controlled via `DEBUG_REQUEST` in `.env` (default: `false`)

### Changed
* Bumped version to `0.2.0`
* Updated `ENVIRONMENT.md` to document new environment variables and usage details



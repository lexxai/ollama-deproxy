# Ollama DeProxy

A lightweight, feature-rich proxy for [**Ollama**][1], designed for development, testing, and staging environments.
It simplifies access to remote **Ollama** instances that are wrapped behind another proxy layer.
Anthropic and OpenAI compatible endpoints, included.

## Why Use It?

If you're a developer working locally and need to access a remote **Ollama** instance that sits behind an application proxy such as [**OpenWebUI**][2], you may encounter:

- Additional authorization requirements
- Wrapped or modified HTTP headers
- Response compression or transformation
- Reverse proxy constraints

`Ollama DeProxy` provides a clean and simple way to:

- Bypass extra authorization layers
- Forward requests transparently
- Control streaming and decoding behavior
- Restore direct API-like access to the upstream Ollama service

It acts as a thin, configurable HTTP bridge between your local tools and the remote Ollama instance.

## Features

- **Transparent Request Forwarding**: Acts as a local HTTP server (default port `11434`) that forwards all requests to a remote Ollama-compatible API
- **Authentication Handling**: Automatically injects custom authentication headers (JWT, API Keys) to bypass upstream proxy layers
- **Response Processing**: Supports streaming, decompression (Brotli/Gzip), and header filtering
- **Model Name Correction**: Replaces numeric model identifiers with actual model names
- **Response Caching**: Caches responses for specific endpoints with TTL-based eviction
- **HTTP/2 Support**: Full support for modern upstream connections.
- **Efficient Decoding**: Use `DECODE_RESPONSE` to choose between automatic decompression (Brotli/Gzip) or raw binary passthrough.
- **Anthropic and OpenAI** compatible endpoints detection

## Quick Start

1. **Clone the repository**:

```bash
git clone https://github.com/lexxai/ollama-deproxy.git
cd ollama-deproxy
```

2. **Configure environment variables**:

```bash
cp .env.example .env
# Edit `.env` with your configuration
```

### Using Docker Compose

Run the following command in your terminal to start the service:

```bash
docker compose up -d
```

This will launch the container with the specified configuration.

#### Verifying the Connection

You can monitor the initialization and incoming traffic by checking the service logs:

```bash
docker compose logs -f
ollama-deproxy-1  | INFO:     Started server process [1]
ollama-deproxy-1  | INFO:     Waiting for application startup.
ollama-deproxy-1  | INFO:     Application startup complete.
ollama-deproxy-1  | INFO:     Uvicorn running on http://0.0.0.0:11434 (Press CTRL+C to quit)
ollama-deproxy-1  | INFO:     172.21.0.1:60700 - "POST /api/generate HTTP/1.1" 200 OK
```

#### Zero-Auth Local Access

Once the container is active, your local applications can communicate with the remote Ollama instance via:

Local Address: http://localhost:11434

Security: The proxy handles all necessary authentication headers upstream, allowing your local tools to connect seamlessly without managing API keys or complex auth logic.

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/lexxai/ollama-deproxy.git
cd ollama-deproxy
```

### Option 1 - Using `uv` _(recommended)_

[`uv`](https://github.com/astral-sh/uv) is a blazing-fast Python package installer and resolver, written in Rust.

1. **Install `uv`** _(if not already installed)_:

```bash
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Set up and sync the environment**:

```bash
uv venv
uv sync
```

3. **Configure environment variables**:

```bash
cp .env.example .env
# Edit `.env` with your configuration
```

4. **Run the server**:

```bash
uv run -m src.ollama_deproxy.main
```

---

### Option 2 - Using `pip` _(fallback)_

If you prefer `pip`, or `uv` is unavailable:

#### Windows

```bash
python -m venv .venv && .venv\Scripts\activate
```

#### macOS / Linux

```bash
python -m venv .venv && source .venv/bin/activate
```

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Configure `.env`**:

```bash
cp .env.example .env
# Edit `.env` as needed
```

3. **Run the server**:

```bash
python -m src.ollama_deproxy.main
```

If installed as a wheel:

```bash
ollama-deproxy
```

---

## Build as a Package

Build and install as a distributable package:

```bash
uv build
# Outputs:
# Successfully built dist/ollama_deproxy-0.1.0.tar.gz
# Successfully built dist/ollama_deproxy-0.1.0-py3-none-any.whl
```

Then run the CLI directly:

```bash
uv run ollama-deproxy
# → INFO:     Started server process [21540]
# → INFO:     Uvicorn running on http://0.0.0.0:11434
```

Expected output:

```
INFO:     Started server process [1422]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:11434 (Press CTRL+C to quit)
INFO:     127.0.0.1:56456 - "GET /api/tags HTTP/1.1" 200 OK
```

## [Environment Configuration](DOCS/ENVIRONMENT.md)

## Response Caching

The proxy includes a built-in caching system to improve performance for frequently accessed endpoints controlled by environment variables:
* **CACHE_ENABLED**
* **CACHE_MAXSIZE**
* **CACHE_TTL**
* **HASH_ALGORITHM**
  Includes automatic hash algorithm detection to identify the optimal cache key generation method for your platform and
  architecture.
    ```bash
    uv run ollama-deproxy
    Ollama DeProxy v0.4.0
    INFO:     Started server process [29256]
    INFO:     Waiting for application startup.
    INFO:ollama_deproxy.best_hash:Cache key hash algorithm auto-selection...
    INFO:ollama_deproxy.cache_base:Cache key hash algorithm auto-selection complete. Can store it on .env file 'HASH_ALGORITHM=blake2b' for skip autodetection next time.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:11434 (Press CTRL+C to quit)
    ```

**Cached Endpoints:**

- `/api/tags` - Model list
- `/api/models` - Model information
- `/api/show` - Model details

**Benefits:**

- Reduces latency for repeated requests
- Decreases load on remote Ollama instances
- Improves response times for model metadata queries

## Error Logging & Diagnostics

When the remote server returns an error (HTTP 400+), the proxy interrupts the stream to capture the full context. This allows you to see exactly why the upstream rejected your request.

**Example Failure:**
If you query a model that doesn't exist on the remote host:

```bash
ERROR:ollama_deproxy.handlers:Remote Error [400] on https://openwebui.example.com/ollama/api/show {"name":"qwen2.5-coder:1.5b-base1"} {"detail":"Model 'qwen2.5-coder:1.5b-base1' was not found"}
```

Where is:

```text
Sent Body: {"name":"qwen2.5-coder:1.5b-base1"}
Recv Body: {"detail":"Model 'qwen2.5-coder:1.5b-base1' was not found"}
```

**Example Debug Log:**
```dotenv
LOG_LEVEL=DEBUG
````
```bash
Ollama DeProxy v0.4.0
2026-03-13 15:34:08 DEBUG:    Starting Ollama DeProxy with DEBUG logging... DEBUG_REQUEST=False,CACHE_ENABLED=True
2026-03-13 15:34:08 INFO:     Started server process [43460]
2026-03-13 15:34:08 INFO:     Waiting for application startup.
2026-03-13 15:34:08 INFO:     Cache key hash algorithm selected: blake2b
2026-03-13 15:34:08 INFO:     Application startup complete.
2026-03-13 15:34:08 INFO:     Uvicorn running on http://0.0.0.0:11434 (Press CTRL+C to quit)
2026-03-13 15:34:57 DEBUG:    *** Finished response for /ollama/api/tags in 00:00.6
2026-03-13 15:34:57 DEBUG:    Cache set for key: ollama/api/tags:get...
2026-03-13 15:34:57 INFO:     127.0.0.1:8327 - "GET /api/tags HTTP/1.1" 200
2026-03-13 15:35:37 DEBUG:    Proxying request corrected to 'api/v1/messages' for Anthropic compatibility
2026-03-13 15:35:37 DEBUG:    *** Handling request for path: /api/v1/messages
2026-03-13 15:36:21 INFO:     127.0.0.1:61399 - "POST /v1/messages?beta=true HTTP/1.1" 200
2026-03-13 15:36:23 DEBUG:    *** Finished up stream for /api/v1/messages in 00:46.1
2026-03-13 15:36:37 DEBUG:    Cache hit for key: ollama/api/tags:get...
2026-03-13 15:36:37 INFO:     127.0.0.1:61402 - "GET /api/tags HTTP/1.1" 200
2026-03-13 15:38:25 DEBUG:    Cache hit for key: ollama/api/tags:get...
2026-03-13 15:38:25 INFO:     127.0.0.1:61408 - "GET /api/tags HTTP/1.1" 200
2026-03-13 15:38:26 DEBUG:    Cache hit for key: ollama/api/tags:get...
2026-03-13 15:38:26 INFO:     127.0.0.1:61411 - "GET /api/tags HTTP/1.1" 200
2026-03-13 15:39:03 DEBUG:    Proxying request corrected to 'ollama/v1/chat/completions' for OpenAI compatibility
2026-03-13 15:39:03 DEBUG:    *** Handling request for path: /ollama/v1/chat/completions
2026-03-13 15:39:13 INFO:     127.0.0.1:61414 - "POST /chat/completions HTTP/1.1" 200
2026-03-13 15:39:13 DEBUG:    *** Finished up stream for /ollama/v1/chat/completions in 00:09.3
2026-03-13 15:41:18 INFO:     Shutting down
2026-03-13 15:41:18 INFO:     Waiting for application shutdown.
2026-03-13 15:41:18 INFO:     Application shutdown complete.
2026-03-13 15:41:18 INFO:     Finished server process [43460]


Sleeping for 10 sec before restarting server. Press Ctrl+C to exit.
Restarting server...
2026-03-13 15:41:28 DEBUG:    Using proactor: IocpProactor
2026-03-13 15:41:28 INFO:     Started server process [43460]
2026-03-13 15:41:28 INFO:     Waiting for application startup.
2026-03-13 15:41:28 INFO:     Cache key hash algorithm selected: blake2b
2026-03-13 15:41:28 INFO:     Application startup complete.
2026-03-13 15:41:28 INFO:     Uvicorn running on http://0.0.0.0:11434 (Press CTRL+C to quit)
```

## CLI Usage
In CLI mode, you can use the `ollama-deproxy` command to start the server. And also can override some environment variables.

```bash
uv run ollama-deproxy --help           
usage: ollama-deproxy [-h] [--remote-url REMOTE_URL] [--remote-auth-token REMOTE_AUTH_TOKEN]
                      [--local-port LOCAL_PORT] [--log-level LOG_LEVEL] [--env_path ENV_PATH] [--version]

Run the Ollama DeProxy application.

options:
  -h, --help            show this help message and exit
  --remote-url REMOTE_URL
                        Override REMOTE_URL environment variable
  --remote-auth-token REMOTE_AUTH_TOKEN
                        Override REMOTE_AUTH_TOKEN environment variable
  --local-port LOCAL_PORT
                        Override local_port environment variable
  --log-level LOG_LEVEL
                        Override log level environment variable
  --env_path ENV_PATH   Override path to .env file
  --version, -v         Version of the application

```


---

## Reference

[1]: https://github.com/ollama/ollama
[2]: https://docs.openwebui.com/reference/api-endpoints#-ollama-api-proxy-support

- https://github.com/ollama/ollama
- https://docs.openwebui.com/reference/api-endpoints#-ollama-api-proxy-support
- https://lexxai.blogspot.com/2026/02/ollama-deproxy-ollama.html
- [https://lexxai.github.io](https://lexxai.github.io/2026/02/25/ollama-deproxy-%D0%B0%D0%B1%D0%BE-%D1%8F%D0%BA-%D0%BE%D1%82%D1%80%D0%B8%D0%BC%D0%B0%D1%82%D0%B8-%D0%BB%D0%BE%D0%BA%D0%B0%D0%BB%D1%8C%D0%BD%D0%B8%D0%B9-%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF-%D0%B4%D0%BE-%D0%B2%D1%96%D0%B4%D0%B4%D0%B0%D0%BB%D0%B5%D0%BD%D0%BE%D1%97-ollama.html)

## License

MIT License — see the [LICENSE](LICENSE) file for details.

# Ollama DeProxy

A lightweight, feature-rich proxy for [**Ollama**][1], designed for development, testing, and staging environments.
It simplifies access to remote **Ollama** instances that are wrapped behind another proxy layer.

## Why Use It?

If you're a developer working locally and need to access a remote **Ollama** instance that sits behind an application proxy such as [**OpenWebUI**][2], you may encounter:

* Additional authorization requirements
* Wrapped or modified HTTP headers
* Response compression or transformation
* Reverse proxy constraints

`Ollama DeProxy` provides a clean and simple way to:

* Bypass extra authorization layers
* Forward requests transparently
* Control streaming and decoding behavior
* Restore direct API-like access to the upstream Ollama service

It acts as a thin, configurable HTTP bridge between your local tools and the remote Ollama instance.

## Features

* **Auth Injection**: Automatically inject custom headers (JWT, API Keys) to bypass upstream proxy layers.
* **Transparent Forwarding**: Supports all HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, etc.).
* **Smart Streaming**: Toggle `STREAM_RESPONSE` to match your client application's requirements.
* **Efficient Decoding**: Use `DECODE_RESPONSE` to choose between automatic decompression (Brotli/Gzip) or raw binary passthrough for lower CPU overhead.
* **HTTP/2 Support**: Full support for modern upstream connections.
---

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

### Option 1 - Using `uv` *(recommended)*

[`uv`](https://github.com/astral-sh/uv) is a blazing-fast Python package installer and resolver, written in Rust.

1. **Install `uv`** *(if not already installed)*:

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

### Option 2 - Using `pip` *(fallback)*

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

##  Build as a Package

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


## Error Logging & Diagnostics

When the remote server returns an error (HTTP 400+), the proxy interrupts the stream to capture the full context. This allows you to see exactly why the upstream rejected your request.

**Example Failure:**
If you query a model that doesn't exist on the remote host:

```text
ERROR:ollama_deproxy.handlers:Remote Error [400] on https://openwebui.example.com/ollama/api/show {"name":"qwen2.5-coder:1.5b-base1"} {"detail":"Model 'qwen2.5-coder:1.5b-base1' was not found"}
```
Where is:
```text
Sent Body: {"name":"qwen2.5-coder:1.5b-base1"}
Recv Body: {"detail":"Model 'qwen2.5-coder:1.5b-base1' was not found"}
```

---

## Reference

[1]: https://github.com/ollama/ollama
[2]: https://docs.openwebui.com/reference/api-endpoints#-ollama-api-proxy-support
* https://github.com/ollama/ollama
* https://docs.openwebui.com/reference/api-endpoints#-ollama-api-proxy-support

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.


# Environment Configuration

`Ollama DeProxy` is fully configured via environment variables.  
Create a `.env` file based on `.env.example` and adjust the values as needed.

---

## Remote Connection (Required)

### `REMOTE_URL` **(required)**  
Remote Ollama API endpoint.

Example:
```bash
REMOTE_URL=https://openwebui.example.com/ollama
````

This should point to the upstream Ollama-compatible API (for example, one exposed by OpenWebUI).

---

### `REMOTE_AUTH_TOKEN`

Authentication token used for the remote API.

Typically in Bearer format:

```bash
REMOTE_AUTH_TOKEN=Bearer YOUR_TOKEN_HERE
```

If the upstream service requires authorization, this token will be injected into outgoing requests.

---

## 🛠️ Optional Configuration

### `LOG_LEVEL`

Logging verbosity.

Default:

```
INFO
```

Available values:

* `DEBUG`
* `INFO`
* `WARNING`
* `ERROR`
* `CRITICAL`

Example:

```bash
LOG_LEVEL=DEBUG
```

---

### `REMOTE_URL_HTTP2`

Enable HTTP/2 for remote connections.

Default:

```
True
```

Disable if the upstream proxy does not properly support HTTP/2:

```bash
REMOTE_URL_HTTP2=False
```

---

### `REMOTE_AUTH_HEADER`

Custom header name used for authentication.

Default:

```
Authorization
```

Example:

```bash
REMOTE_AUTH_HEADER=X-API-Key
```

---

### `LOCAL_PORT`

Port the proxy listens on locally.

Default:

```
11434
```

Example:

```bash
LOCAL_PORT=8080
```

---

### `REMOTE_TIMEOUT`

Timeout (in seconds) for upstream requests.

* Leave empty for no timeout.
* Set a numeric value to enforce request limits.

Example:

```bash
REMOTE_TIMEOUT=60
```

---

### `STREAM_RESPONSE`

Control streaming behavior for remote responses.

Default:

```
True
```

* `True` → Stream responses directly (recommended for chat/completions)
* `False` → Buffer full response before returning

Example:

```bash
STREAM_RESPONSE=False
```

---

### `DECODE_RESPONSE`

Advanced option: Automatically decode `br` (Brotli) and `zstd` compressed responses.

Default:

```
False
```

Enable if your upstream proxy applies compression that must be removed:

```bash
DECODE_RESPONSE=True
```

> Enable only if you explicitly need response decompression before forwarding.

Enable debugging for incoming requests (default: False)
```bash
#DEBUG_REQUEST=False
```

If models are numbered, try to replace them to string representation of an Ollama list.
This is useful for Copilot Plugin from GitHub that uses numbered model names instead of string.
Default: False
```bash
CORRECT_NUMBERED_MODEL_NAMES=False
```

When enabled,
```bash
CORRECT_NUMBERED_MODEL_NAMES=True
```
In logs can see:
```text
DEBUG:ollama_deproxy.ollama_helper:0:qwen2.5-coder:1.5b-base
DEBUG:ollama_deproxy.ollama_helper:1:qwen3:30b
DEBUG:ollama_deproxy.ollama_helper:2:qwen3:14b
DEBUG:ollama_deproxy.ollama_helper:3:qwen3:8b
DEBUG:ollama_deproxy.ollama_helper:4:qwen3-coder-next:latest
DEBUG:ollama_deproxy.ollama_helper:5:qwen2.5:0.5b
DEBUG:ollama_deproxy.ollama_helper:6:johanteekens/Llama-4-Scout-17B-16E-Instruct:latest
DEBUG:ollama_deproxy.ollama_helper:7:qwen3-embedding:latest
DEBUG:ollama_deproxy.ollama_helper:8:qwen3-embedding:4b
DEBUG:ollama_deproxy.ollama_helper:9:qwen3-embedding:0.6b
DEBUG:ollama_deproxy.ollama_helper:10:phi4:14b
DEBUG:ollama_deproxy.ollama_helper:11:phi3:3.8b
DEBUG:ollama_deproxy.ollama_helper:12:phi3:14b
DEBUG:ollama_deproxy.ollama_helper:13:paraphrase-multilingual:latest
DEBUG:ollama_deproxy.ollama_helper:14:nomic-embed-text:latest
DEBUG:ollama_deproxy.ollama_helper:15:mxbai-embed-large:latest
DEBUG:ollama_deproxy.ollama_helper:16:mistral:latest
DEBUG:ollama_deproxy.ollama_helper:17:llava:7b
DEBUG:ollama_deproxy.ollama_helper:18:llama3.2:3b
DEBUG:ollama_deproxy.ollama_helper:19:llama3.1:8b
DEBUG:ollama_deproxy.ollama_helper:20:granite-embedding:30m
DEBUG:ollama_deproxy.ollama_helper:21:granite-embedding:278m
DEBUG:ollama_deproxy.ollama_helper:22:gpt-oss:20b
DEBUG:ollama_deproxy.ollama_helper:23:gemma3:27b
DEBUG:ollama_deproxy.ollama_helper:24:gemma3:12b-it-qat
DEBUG:ollama_deproxy.ollama_helper:25:gemma3:12b
DEBUG:ollama_deproxy.ollama_helper:26:embeddinggemma:latest
DEBUG:ollama_deproxy.ollama_helper:27:dengcao/Qwen3-Reranker-0.6B:Q8_0
DEBUG:ollama_deproxy.ollama_helper:28:deepseek-r1:8b
DEBUG:ollama_deproxy.ollama_helper:29:codellama:34b-instruct
DEBUG:ollama_deproxy.ollama_helper:30:chroma/all-minilm-l6-v2-f32:latest
````
```text
DEBUG:ollama_deproxy.ollama_helper:replacement model_name: qwen3-coder-next:latest for 4
```




---

## Minimal Required Configuration

At minimum, you must define:

```bash
REMOTE_URL=...
```

Everything else has safe defaults.

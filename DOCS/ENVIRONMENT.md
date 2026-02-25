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

---

## Minimal Required Configuration

At minimum, you must define:

```bash
REMOTE_URL=...
```

Everything else has safe defaults.

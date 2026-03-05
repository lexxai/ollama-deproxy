from starlette.requests import Request


def get_http_connection(request: Request):
    app = request.app
    return app.state.http_connection


def get_ollama_helper(request: Request):
    app = request.app
    return app.state.ollama_helper


def get_response_cache(request: Request):
    app = request.app
    return app.state.response_cache


def get_semaphore(request: Request):
    app = request.app
    return app.state.semaphore

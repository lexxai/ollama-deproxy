from starlette.requests import Request


def get_session(request: Request):
    app = request.app
    return app.state.session


def get_ollama_helper(request: Request):
    app = request.app
    return app.state.ollama_helper


def get_response_cache(request: Request):
    app = request.app
    return app.state.response_cache
